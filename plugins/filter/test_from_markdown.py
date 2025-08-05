from __future__ import annotations

import pytest
from plugins.filter.from_markdown import from_markdown, fstab_extract_mounts, FilterModule


def test_filters_registry_contains_from_markdown() -> None:
    fm = FilterModule()
    filters = fm.filters()
    assert "from_markdown" in filters
    assert callable(filters["from_markdown"])
    assert "fstab_extract_mounts" in filters
    assert callable(filters["fstab_extract_mounts"])


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        ("```hello```", "hello\n"),
        ("~~~hello~~~", "hello\n"),
        ("```hello", "hello\n"),
        ("hello```", "hello\n"),
        ("~~~hello", "hello\n"),
        ("hello~~~", "hello\n"),
        ("  hello  ", "hello\n"),
        ("\nhello\n", "hello\n"),
        ("```  hello  ```", "hello\n"),
    ],
)
def test_from_markdown_strips_fences_and_trims(input_text: str, expected: str) -> None:
    assert from_markdown(input_text) == expected


def test_fstab_extract_mounts_skips_comments_and_blank() -> None:
    data = """# comment
UUID=111 / ext4 defaults 0 1

tmpfs /run tmpfs defaults 0 0
"""
    assert fstab_extract_mounts(data) == ["/", "/run"]


def test_fstab_extract_mounts_simple() -> None:
    data = "UUID=222 /var ext4 defaults 0 2\n/dev/sda1 /boot vfat defaults 0 2"
    assert fstab_extract_mounts(data) == ["/var", "/boot"]
