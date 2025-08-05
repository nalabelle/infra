from __future__ import annotations

import json
from subprocess import PIPE, Popen
from typing import TypedDict, cast

import yaml
from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, Constructable
from ansible.utils.display import Display


class HostDict(TypedDict):
    name: str
    ansible_vars: dict[str, str]
    groups: list[str]


class SectionDict(TypedDict):
    id: str


# Base TypedDict with required fields
class FieldDictRequired(TypedDict):
    label: str


# Derived TypedDict with optional fields
class FieldDict(FieldDictRequired, total=False):
    value: str
    section: SectionDict


class ItemDict(TypedDict, total=False):
    title: str
    fields: list[FieldDict]


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


class OnePass:
    bin = "op"
    default_args: tuple[str] = ("--format=json",)

    def __init__(self, vault: str | None = None) -> None:
        self.args = list(self.default_args)
        if vault:
            self.args.append(f"--vault={vault}")

    def assert_logged_in(self) -> bool:
        # Don't use default_args here, because we need to skip the vault option
        args = ["account", "get", "--format=json"]
        out = self._run(args, ignore_errors=True)
        result = json.loads(out)
        if not result.get("state"):
            raise AnsibleError("You must be logged in to an active 1Password account.")
        return True

    def get_item(self, item_id: str) -> str:
        args = ["item", "get", item_id]
        return self._run(args + self.args)

    def list_servers(self) -> str:
        args = ["item", "list", "--categories=SERVER"]
        return self._run(args + self.args)

    def _run(
        self, args: list[str], expected_rc: int = 0, command_input: str | None = None, ignore_errors: bool = False
    ) -> str:
        command = [self.bin, *args]
        p = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True, encoding="utf-8")
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
    ) -> None:
        self.name = name
        self.ansible_vars = ansible_vars
        self.groups = groups

    def to_dict(self) -> HostDict:
        """Convert Host object to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "ansible_vars": self.ansible_vars,
            "groups": self.groups,
        }

    @staticmethod
    def from_dict(data: HostDict) -> Host:
        """Create Host object from dictionary"""
        return Host(
            name=data["name"],
            ansible_vars=data["ansible_vars"],
            groups=data["groups"],
        )

    @staticmethod
    def from_op(item: ItemDict) -> Host:
        name = item.get("title")
        if not name:
            raise AnsibleError("Title not found in op item")
        fields = Host.transform_fields(item.get("fields", []))
        # Ensure ansible_hostname is a string
        url_value = fields.get("url", "")
        ansible_hostname = url_value if isinstance(url_value, str) else ""

        # Get ansible key and validate it's a string
        ansible_key = fields.get("ansible", "")
        if not isinstance(ansible_key, str):
            raise AnsibleError("Ansible key had dict, expected string")

        # Use cast to tell the type checker that ansible_vars is dict[str, str]
        ansible_vars = cast(dict[str, str], yaml.safe_load(ansible_key) or {})

        # Add ansible_host if hostname is available
        if ansible_hostname:
            ansible_vars["ansible_host"] = ansible_hostname

        # Handle the case where groups might be a dict or a str
        groups_value = fields.get("groups", "")
        if isinstance(groups_value, str):
            groups = [group.strip() for group in groups_value.split(",") if len(group.strip()) > 0]
        else:
            groups = []

        return Host(name, ansible_vars, groups)

    @staticmethod
    def transform_fields(
        fields: list[FieldDict],
    ) -> dict[str, dict[str, str] | str]:
        result: dict[str, dict[str, str] | str] = {}
        sections: dict[str, dict[str, str]] = {}

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

    def __init__(self) -> None:
        super().__init__()
        self.hosts: list[Host] = []
        self.cache_key: str | None = None
        self.use_cache = False
        self.display = Display()

    def _load_from_onepassword(self) -> list[Host]:
        hosts = []
        server_ids = [server["id"] for server in json.loads(self.op.list_servers())]
        for id in server_ids:
            item = json.loads(self.op.get_item(id))
            host = Host.from_op(item)
            hosts.append(host)
        return hosts

    def populate(self) -> None:
        if not self.inventory:
            raise AnsibleError("Inventory not initialized")

        for host in self.hosts:
            self.inventory.add_host(host.name)
            for group in host.groups:
                groups = self.inventory.get_groups_dict()
                if group not in groups.keys():
                    self.inventory.add_group(group)
                self.inventory.add_child(group, host.name)
            for key, value in host.ansible_vars.items():
                self.inventory.set_variable(host.name, key, value)

    def verify_file(self, path: str) -> bool:
        """return true/false if this is possibly a valid file for this plugin to consume"""
        if super().verify_file(path):
            if path.endswith(("onepassword.yml", "onepassword.yaml")):
                return True
            else:
                self.display.vvv("Inventory source not ending in 'onepassword.yml' or 'onepassword.yaml'")
        return False

    def parse(self, inventory: object, loader: object, path: str, cache: bool = True) -> None:
        super().parse(inventory, loader, path)
        self.instances = None
        self._read_config_data(path)

        self.op = OnePass(vault=self.get_option("vault"))
        self.op.assert_logged_in()

        self.cache_key = self.get_cache_key(path)
        if cache:
            self.use_cache = self.get_option("cache")
            if self.use_cache:
                cache_data = self._cache.get(self.cache_key) or []
                for host_data in cache_data:
                    try:
                        # Ensure host_data conforms to HostDict structure
                        if (
                            isinstance(host_data, dict)
                            and "name" in host_data
                            and "ansible_vars" in host_data
                            and "groups" in host_data
                            and isinstance(host_data["groups"], list)
                        ):
                            host = Host.from_dict(cast(HostDict, host_data))
                            self.hosts.append(host)
                        else:
                            raise TypeError("Invalid host data structure")
                    except Exception:
                        self.hosts = []
                        break

        if not self.hosts:
            self.hosts = self._load_from_onepassword()
            if self.use_cache:
                self._cache[self.cache_key] = [host.to_dict() for host in self.hosts]

        self.populate()
