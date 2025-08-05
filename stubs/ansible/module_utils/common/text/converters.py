"""Ansible module_utils.common.text.converters stubs."""

from typing import Any


def to_native(obj: Any, encoding: str = "utf-8", errors: str = "surrogate_or_strict") -> str:
    """Convert an object to a native string."""
    return str(obj)
