import unittest
from unittest.mock import patch, Mock
from lib.nextdns import Tracker, Rewrite
from lib.nextdns_config import NextDNSConfig


class TestNextDNSRewriteTool(unittest.TestCase):
    def setUp(self):
        # Mock the NextDNS API responses
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_response.text = ""
        mock_response.status_code = 200

        # Create mock config
        mock_config = Mock(spec=NextDNSConfig)
        mock_config.id = "test_id"
        mock_config.email = "test@example.com"
        mock_config.password = "test_password"

        with (
            patch("requests.Session.get", return_value=mock_response),
            patch("requests.Session.post", return_value=mock_response),
        ):
            self.tracker = Tracker(mock_config)

    def test_read_rewrites(self):
        # Test data mimicking the format in the rewrites file
        mock_file_content = """
# Comment
10.0.1.100               host1.example.com
fd12:3456:789a:1::1      host2.example.com
192.168.1.50             host3.example.com
"""

        expected_output = [
            Rewrite(
                id="",
                name="host1.example.com",
                type="A",
                content="10.0.1.100",
                seen=False,
            ),
            Rewrite(
                id="",
                name="host2.example.com",
                type="AAAA",
                content="fd12:3456:789a:1::1",
                seen=False,
            ),
            Rewrite(
                id="",
                name="host3.example.com",
                type="A",
                content="192.168.1.50",
                seen=False,
            ),
        ]

        # Test reading from content
        rewrites = self.tracker.read_rewrites_from_file(content=mock_file_content)
        self.assertEqual(rewrites, expected_output)


if __name__ == "__main__":
    unittest.main()
