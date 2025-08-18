from __future__ import annotations

import pytest
from ansible.errors import AnsibleFilterError

from plugins.filter.mandatory import FilterModule, very_mandatory


def test_filters_registry_contains_very_mandatory() -> None:
    fm = FilterModule()
    filters = fm.filters()
    assert "very_mandatory" in filters
    assert callable(filters["very_mandatory"])


def test_very_mandatory_passes_non_empty_string() -> None:
    assert very_mandatory("value") == "value"


def test_very_mandatory_raises_when_none_with_default_message() -> None:
    # When None, Ansible's core 'mandatory' filter raises before our empty-string check
    with pytest.raises(AnsibleFilterError) as ei:
        very_mandatory(None)  # type: ignore[arg-type]
    # Error message varies slightly across Ansible versions; assert prefix
    assert "Mandatory" in str(ei.value)


def test_very_mandatory_raises_when_empty_string_default_message() -> None:
    # very_mandatory raises ansible.errors.AnsibleFilterError
    with pytest.raises(AnsibleFilterError) as ei:
        very_mandatory("")
    assert "Mandatory variable is empty" in str(ei.value)


def test_very_mandatory_raises_when_empty_string_custom_message() -> None:
    # Custom message should be propagated through to_native and raised
    with pytest.raises(AnsibleFilterError) as ei:
        very_mandatory("", msg="Custom error")
    assert "Custom error" in str(ei.value)
