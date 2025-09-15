"""Clipboard-related exceptions."""


class ClipboardError(Exception):
    """Base exception for clipboard-related errors."""

    pass


class ClipboardUnavailableError(ClipboardError):
    """Exception raised when copykitten is not available."""

    pass


class ClipboardOperationError(ClipboardError):
    """Exception raised when clipboard operations fail."""

    pass
