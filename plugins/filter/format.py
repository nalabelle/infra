from collections.abc import Callable
from typing import Any


def format_list(list_: list[str], pattern: str) -> list[str]:
    """Formats each item in a list according to pattern provided

    Args:
        list_ (list[str]): list of strings to insert into format pattern
        pattern (str): format pattern to apply to each string

    Returns:
        list[str]: list of strings formatted per pattern
    """
    return [pattern % s for s in list_]


class FilterModule:
    def filters(self) -> dict[str, Callable[..., Any]]:
        return {
            "format_list": format_list,
        }
