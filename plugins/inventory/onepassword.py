from __future__ import absolute_import, division, print_function, annotations
import json
import yaml

from subprocess import Popen, PIPE

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.utils.display import Display
from ansible.errors import AnsibleError

__metaclass__ = type

DOCUMENTATION = """
name: onepassword
plugin_type: inventory
short_description: 1Password dynamic inventory plugin
requirements:
  - op: 1Password CLI
description:
  - Fetches hosts and config from 1Password
  - Uses a YAML configuration file that ends with onepassword.(yml|yaml)
extends_documentation_fragment:
  - constructed
  - inventory_cache
options:
    cache:
        version_added: 0.0.1
    cache_plugin:
        version_added: 0.0.1
    cache_timeout:
        version_added: 0.0.1
    cache_connection:
        version_added: 0.0.1
    cache_prefix:
        version_added: 0.0.1
    plugin:
        description: Token that ensures this is a source file for the 'onepassword' plugin.
        required: True
        choices: ['onepassword']
    vault:
        description: Vault containing the servers to retrieve (case-insensitive). If absent will search all vaults.
        required: False
        type: string
"""

display = Display()


class OnePass(object):
    bin = "op"
    default_args = ["--format=json"]

    def __init__(self, vault=None):
        if vault:
            self.default_args += [f"--vault={vault}"]

    def assert_logged_in(self) -> bool:
        # Don't use default_args here, because we need to skip the vault option
        args = ["account", "get", "--format=json"]
        out = self._run(args, ignore_errors=True)
        result = json.loads(out)
        if not result.get("state"):
            raise AnsibleError("You must be logged in to an active 1Password account.")
        return True

    def get_item(self, item_id) -> str:
        args = ["item", "get", item_id]
        output = self._run(args + self.default_args)
        return output

    def list_servers(self) -> str:
        args = ["item", "list", "--categories=SERVER"]
        output = self._run(args + self.default_args)
        return output

    def _run(self, args, expected_rc=0, command_input=None, ignore_errors=False):
        command = [self.bin] + args
        p = Popen(
            command, stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True, encoding="utf-8"
        )
        out, err = p.communicate(input=command_input)
        rc = p.wait()
        if not ignore_errors and rc != expected_rc:
            raise AnsibleError(err)
        if err:
            display.vvv(err)
        return out


class Host:
    """Represents a host in the inventory"""

    def __init__(
        self,
        name: str,
        ansible_vars: dict[str, str],
        groups: list[str],
    ):
        self.name = name
        self.ansible_vars = ansible_vars
        self.groups = groups

    def to_dict(self) -> dict:
        """Convert Host object to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "ansible_vars": self.ansible_vars,
            "groups": self.groups,
        }

    @staticmethod
    def from_dict(data: dict) -> Host:
        """Create Host object from dictionary"""
        return Host(
            name=data["name"],
            ansible_vars=data["ansible_vars"],
            groups=data["groups"],
        )

    @staticmethod
    def from_op(item: dict) -> Host:
        name = item.get("title", id)
        fields = Host.transform_fields(item.get("fields", []))
        ansible_hostname = fields.get("url", "")
        ansible_vars = yaml.safe_load(fields.get("ansible", "")) or {}
        if ansible_hostname:
            ansible_vars["ansible_host"] = ansible_hostname
        groups = [
            group.strip()
            for group in fields.get("groups", "").split(",")
            if len(group.strip()) > 0
        ]
        return Host(name, ansible_vars, groups)

    @staticmethod
    def transform_fields(
        fields: list[dict[str, str]],
    ) -> dict[str, dict[str, str] | str]:
        result = {}
        sections = {}

        for field in fields:
            if "section" in field:
                section_id = field["section"]["id"]
                if section_id == "add more":
                    result[field["label"].lower()] = field.get("value", "")
                    continue
                if section_id not in sections:
                    sections[section_id] = {}
                sections[section_id][field["label"].lower()] = field.get("value", "")
            else:
                result[field["label"].lower()] = field.get("value", "")

        # Add sections to main result
        result.update(sections)
        return result


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = "onepassword"
    OPTIONS = "VAULT"

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.hosts = []
        self.cache_key = None
        self.use_cache = False

    def _load_from_onepassword(self) -> list[Host]:
        hosts = []
        server_ids = [server["id"] for server in json.loads(self.op.list_servers())]
        for id in server_ids:
            item = json.loads(self.op.get_item(id))
            host = Host.from_op(item)
            hosts.append(host)
        return hosts

    def populate(self) -> None:
        for host in self.hosts:
            self.inventory.add_host(host.name)
            for group in host.groups:
                groups = self.inventory.get_groups_dict()
                if group not in groups.keys():
                    self.inventory.add_group(group)
                self.inventory.add_child(group, host.name)
            for key, value in host.ansible_vars.items():
                self.inventory.set_variable(host.name, key, value)

    def verify_file(self, path) -> bool:
        """return true/false if this is possibly a valid file for this plugin to consume"""
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(("onepassword.yml", "onepassword.yaml")):
                return True
            else:
                self.display.vvv(
                    "Inventory source not ending in 'onepassword.yml' or 'onepassword.yaml'"
                )
        return False

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        self.instances = None
        self._read_config_data(path)

        self.op = OnePass(vault=self.get_option("vault"))
        self.op.assert_logged_in()

        self.cache_key = self.get_cache_key(path)
        if cache:
            self.use_cache = self.get_option("cache")
            if self.use_cache:
                for host_data in self._cache.get(self.cache_key, []):
                    try:
                        host = Host.from_dict(host_data)
                        self.hosts.append(host)
                    except Exception:
                        self.hosts = []
                        break

        if not self.hosts:
            self.hosts = self._load_from_onepassword()
            if self.use_cache:
                self._cache[self.cache_key] = [host.to_dict() for host in self.hosts]

        self.populate()
