"""Clipboard functionality for Lox password manager using CopyKitten."""

import logging
from typing import Optional

from .exceptions import (ClipboardError, ClipboardOperationError,
                         ClipboardUnavailableError)
from .services.manager import ClipboardManager

logger = logging.getLogger(__name__)

_clipboard_manager: Optional[ClipboardManager] = None


def get_clipboard_manager() -> ClipboardManager:
    """
    Get the global clipboard manager instance.

    Returns:
        ClipboardManager: The clipboard manager instance

    Raises:
        ClipboardUnavailableError: If clipboard functionality is not available
    """
    global _clipboard_manager
    if _clipboard_manager is None:
        _clipboard_manager = ClipboardManager()

    if not _clipboard_manager.is_available():
        raise ClipboardUnavailableError(
            "Clipboard functionality not available. "
            "Please install copykitten: pip install copykitten"
        )

    return _clipboard_manager


def copy_to_clipboard(text: str, silent: bool = False) -> bool:
    """
    Copy text to clipboard (convenience function).

    Args:
        text: Text to copy to clipboard
        silent: If True, suppress error logging and exceptions

    Returns:
        bool: True if successful, False otherwise

    Example:
        >>> copy_to_clipboard("my password")
        True
    """
    try:
        manager = get_clipboard_manager()
        return manager.copy(text, silent)
    except ClipboardUnavailableError:
        if not silent:
            logger.error("Clipboard not available")
        return False
    except Exception as e:
        if not silent:
            logger.error("Unexpected clipboard error: %s", e)
        return False


def is_clipboard_available() -> bool:
    """
    Check if clipboard functionality is available.

    Returns:
        bool: True if copykitten is available and functional
    """
    try:
        manager = get_clipboard_manager()
        return manager.is_available()
    except ClipboardUnavailableError:
        return False
    except Exception:
        return False


def get_clipboard_info() -> str:
    """
    Get information about the clipboard service.

    Returns:
        str: Service information string
    """
    try:
        manager = get_clipboard_manager()
        return manager.get_service_info()
    except ClipboardUnavailableError:
        return "Clipboard service: Not available"
    except Exception as e:
        return f"Clipboard service: Error ({e})"


copy_to_clipboard = copy_to_clipboard


__all__ = [
    "copy_to_clipboard",
    "is_clipboard_available",
    "get_clipboard_info",
    "get_clipboard_manager",
    "ClipboardError",
    "ClipboardUnavailableError",
    "ClipboardOperationError",
]
