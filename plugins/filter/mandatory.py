from collections.abc import Callable
from typing import Any

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.filter.core import mandatory


def very_mandatory(a: str, msg: str | None = None) -> str:
    """Make a variable mandatory and raise an error if it is not defined _or is empty string_."""

    # Run ansible's mandatory filter
    a = mandatory(a)
    if a == "":
        if msg is not None:
            raise AnsibleFilterError(to_native(msg))
        raise AnsibleFilterError("Mandatory variable is empty")

    return a


class FilterModule:
    def filters(self) -> dict[str, Callable[..., Any]]:
        return {"very_mandatory": very_mandatory}
