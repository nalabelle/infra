import unittest
from unittest.mock import patch
from lib.onepassword import OnePasswordClient


class TestOnePasswordClient(unittest.TestCase):
    def test_get_field(self):
        def mock_op_item_get(*args, **kwargs):
            class MockResult:
                stdout = '{"value": "test_value"}'
                stderr = ""

            return MockResult()

        with patch("subprocess.run", side_effect=mock_op_item_get):
            client = OnePasswordClient()
            value = client.get_field("test_item", "test_field")
            self.assertEqual(value, "test_value")

    def test_get_field_with_backticks(self):
        def mock_op_item_get(*args, **kwargs):
            class MockResult:
                stdout = '{"value": "```secret_value```"}'
                stderr = ""

            return MockResult()

        with patch("subprocess.run", side_effect=mock_op_item_get):
            client = OnePasswordClient()
            value = client.get_field("test_item", "test_field")
            self.assertEqual(value, "secret_value")

    def test_get_field_with_tildes(self):
        def mock_op_item_get(*args, **kwargs):
            class MockResult:
                stdout = '{"value": "~~~another_secret~~~"}'
                stderr = ""

            return MockResult()

        with patch("subprocess.run", side_effect=mock_op_item_get):
            client = OnePasswordClient()
            value = client.get_field("test_item", "test_field")
            self.assertEqual(value, "another_secret")

    def test_get_fields(self):
        def mock_op_item_get(*args, **kwargs):
            class MockResult:
                stdout = '[{"label": "field1", "value": "value1"}, {"label": "field2", "value": "value2"}]'
                stderr = ""

            return MockResult()

        with patch("subprocess.run", side_effect=mock_op_item_get):
            client = OnePasswordClient()
            values = client.get_fields("test_item", ["field1", "field2"])
            self.assertEqual(values, {"field1": "value1", "field2": "value2"})

    def test_get_fields_with_formatting(self):
        def mock_op_item_get(*args, **kwargs):
            class MockResult:
                stdout = '[{"label": "field1", "value": "```secret1```"}, {"label": "field2", "value": "~~~secret2~~~"}]'
                stderr = ""

            return MockResult()

        with patch("subprocess.run", side_effect=mock_op_item_get):
            client = OnePasswordClient()
            values = client.get_fields("test_item", ["field1", "field2"])
            self.assertEqual(values, {"field1": "secret1", "field2": "secret2"})
