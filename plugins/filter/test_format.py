from __future__ import annotations

import pytest
from plugins.filter.format import format_list, FilterModule


def test_filters_registry_contains_format_list() -> None:
    fm = FilterModule()
    filters = fm.filters()
    assert "format_list" in filters
    assert filters["format_list"] is format_list


def test_format_list_basic() -> None:
    assert format_list(["a", "b"], "x%sx") == ["xax", "xbx"]


def test_format_list_empty_list() -> None:
    assert format_list([], "[%s]") == []


def test_format_list_numeric_like_strings() -> None:
    assert format_list(["1", "2", "3"], "#%s") == ["#1", "#2", "#3"]
