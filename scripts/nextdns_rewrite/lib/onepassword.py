import json
import subprocess
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class OnePasswordClient:
    """Client for interacting with 1Password CLI."""

    def __init__(self, vault: str = "Applications"):
        self.vault = vault

    def _strip_formatting(self, value: str) -> str:
        """Remove formatting tags from a value.

        Args:
            value: Value to strip formatting from

        Returns:
            str: Value with formatting tags removed
        """
        if value.startswith("```"):
            value = value[3:]
        if value.endswith("```"):
            value = value[:-3]
        if value.startswith("~~~"):
            value = value[3:]
        if value.endswith("~~~"):
            value = value[:-3]
        return value.strip()

    def get_field(self, item_name: str, field_name: str) -> str:
        """Get a single field from a 1Password item.

        Args:
            item_name: Name of the item to get
            field_name: Name of the field to get

        Returns:
            str: Value of the field
        """
        try:
            result = subprocess.run(
                [
                    "op",
                    "item",
                    "get",
                    item_name,
                    f"--vault={self.vault}",
                    "--fields",
                    field_name,
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            value = json.loads(result.stdout)["value"]
            return self._strip_formatting(value)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get item {item_name} from 1Password: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse 1Password output as JSON: {e}")
            raise

    def get_fields(self, item_name: str, field_names: List[str]) -> Dict[str, str]:
        """Get multiple fields from a 1Password item.

        Args:
            item_name: Name of the item to get
            field_names: List of field names to get

        Returns:
            Dict[str, str]: Dictionary mapping field names to their values
        """
        try:
            result = subprocess.run(
                [
                    "op",
                    "item",
                    "get",
                    item_name,
                    f"--vault={self.vault}",
                    "--fields",
                    ",".join(field_names),
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            response = json.loads(result.stdout)
            if isinstance(response, list):
                return {
                    item["label"]: self._strip_formatting(item["value"])
                    for item in response
                }
            raise ValueError(
                f"Expected list response for multiple fields, got {type(response)}"
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get item {item_name} from 1Password: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse 1Password output as JSON: {e}")
            raise
