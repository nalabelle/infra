from lib.onepassword import OnePasswordClient


class NextDNSConfig:
    """Client for retrieving NextDNS configuration from 1Password."""

    def __init__(self) -> None:
        onepassword = OnePasswordClient()
        # Get DNS rewrites
        self._dns_rewrites: str = onepassword.get_field("DNS Rewrites", "notesPlain")

        # Get NextDNS credentials
        values: dict[str, str] = onepassword.get_fields("NextDNS", ["prefix", "email", "password"])
        self._id: str = values["prefix"]
        self._email: str = values["email"]
        self._password: str = values["password"]

    @property
    def email(self) -> str:
        """Get NextDNS email."""
        return self._email

    @property
    def password(self) -> str:
        """Get NextDNS password."""
        return self._password

    @property
    def id(self) -> str:
        """Get NextDNS ID."""
        return self._id

    @property
    def dns_rewrites(self) -> str:
        """Get DNS rewrites."""
        return self._dns_rewrites
