from collections.abc import Callable
from typing import Any

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.filter.core import mandatory


def very_mandatory(a: str, msg: str | None = None) -> str:
    """Make a variable mandatory and raise an error if it is not defined, is None, or is empty string."""
    # Run ansible's mandatory filter (raises on undefined)
    a = mandatory(a)
    if a is None or a == "":
        raise AnsibleFilterError(to_native(msg) if msg is not None else "Mandatory variable is empty")
    return a


class FilterModule:
    def filters(self) -> dict[str, Callable[..., Any]]:
        return {"very_mandatory": very_mandatory}
