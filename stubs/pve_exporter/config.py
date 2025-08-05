"""Stub for pve_exporter.config module."""

from collections.abc import Mapping
from typing import Any


def config_from_env(env: Mapping[str, str]) -> dict[str, dict[str, Any]]:
    """Create PVE configuration from environment variables.

    Args:
        env: Environment variables

    Returns:
        PVE configuration
    """
    return {"default": {}}
