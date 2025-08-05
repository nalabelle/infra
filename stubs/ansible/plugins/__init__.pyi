from typing import Any

class AnsiblePlugin:
    """Base class for all Ansible plugins."""

    def get_option(
        self, option: str, hostvars: dict[str, Any] | None = None, variables: dict[str, Any] | None = None
    ) -> Any: ...
