from collections.abc import Callable
from typing import Any


def from_markdown(a: str, msg: str | None = None) -> str:
    """Strip formatting tags from markdown text. This makes it easier to edit in 1password."""

    if a.startswith("```"):
        a = a[3:]
    if a.endswith("```"):
        a = a[:-3]
    if a.startswith("~~~"):
        a = a[3:]
    if a.endswith("~~~"):
        a = a[:-3]
    a = a.strip() + "\n"
    return a


def fstab_extract_mounts(a: str) -> list[str]:
    mounts = []
    # In fstab format, the second field is the mount point
    for row in a.split("\n"):
        if row.startswith("#") or row.strip() == "":
            continue
        mounts.append(row.split()[1])
    return mounts


class FilterModule:
    def filters(self) -> dict[str, Callable[..., Any]]:
        return {
            "from_markdown": from_markdown,
            "fstab_extract_mounts": fstab_extract_mounts,
        }
