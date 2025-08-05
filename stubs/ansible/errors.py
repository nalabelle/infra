"""Ansible errors stubs."""

from typing import Any


class AnsibleError(Exception):
    """Base class for Ansible errors."""

    def __init__(self, message: str, obj: Any | None = None) -> None:
        self.message = message
        self.obj = obj
        super().__init__(message)


class AnsibleFilterError(AnsibleError):
    """Error from an Ansible filter plugin."""

    pass
