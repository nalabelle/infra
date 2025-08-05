#!/usr/bin/env python3
import pytest

from plugins.inventory.onepassword import OnePass


def test_onepass_run() -> None:
    """Test that the OnePass._run method works correctly."""
    # Create an instance of OnePass
    op = OnePass(vault="Applications")

    # Run a simple command
    result = op._run(["--version"])

    # Check that the result is not empty
    assert result.strip() != ""

    # Check that the result is a string
    assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
