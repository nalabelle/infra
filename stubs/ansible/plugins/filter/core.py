"""Ansible plugins.filter.core stubs."""

from typing import Any


def mandatory(a: Any) -> Any:
    """Make a variable mandatory."""
    if a is None:
        raise ValueError("Mandatory variable is not defined")
    return a
