"""Ansible display stubs."""


class Display:
    """Display class for Ansible."""

    def __init__(self) -> None:
        pass

    def vvv(self, msg: str, host: str | None = None) -> None:
        """Display a verbose message."""
        pass

    def verbose(self, msg: str, host: str | None = None) -> None:
        """Display a verbose message."""
        pass

    def debug(self, msg: str, host: str | None = None) -> None:
        """Display a debug message."""
        pass

    def warning(self, msg: str, host: str | None = None) -> None:
        """Display a warning message."""
        pass

    def error(self, msg: str, host: str | None = None) -> None:
        """Display an error message."""
        pass
