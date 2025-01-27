import unittest
from unittest.mock import Mock, patch
from lib.onepassword import OnePasswordClient
from lib.nextdns_config import NextDNSConfig


class TestNextDNSConfig(unittest.TestCase):
    def test_init_loads_all_values(self):
        # Mock the 1Password responses
        mock_credentials = {
            "prefix": "test_id",
            "email": "test@example.com",
            "password": "test_password",
        }
        mock_rewrites = """
# Comment
10.0.1.100               host1.example.com
fd12:3456:789a:1::1      host2.example.com
192.168.1.50             host3.example.com

server1.example.com       app1.example.com
"""
        # Create mock client
        mock_onepassword = Mock(spec=OnePasswordClient)
        mock_onepassword.get_field.return_value = mock_rewrites
        mock_onepassword.get_fields.return_value = mock_credentials

        with patch("lib.nextdns_config.OnePasswordClient", return_value=mock_onepassword):
            config = NextDNSConfig()

            # Verify correct calls were made
            mock_onepassword.get_field.assert_called_once_with(
                "DNS Rewrites", "notesPlain"
            )
            mock_onepassword.get_fields.assert_called_once_with(
                "NextDNS", ["prefix", "email", "password"]
            )

            # Check credentials
            self.assertEqual(config.email, "test@example.com")
            self.assertEqual(config.password, "test_password")

            # Check nextdns_id
            self.assertEqual(config.id, "test_id")

            # Check dns_rewrites
            self.assertEqual(config.dns_rewrites.strip(), mock_rewrites.strip())
