import logging
from contextlib import contextmanager
from typing import Optional

from ..exceptions import ClipboardOperationError, ClipboardUnavailableError
from .copykitten_service import CopyKittenService

logger = logging.getLogger(__name__)


class ClipboardManager:
    """Manages clipboard operations using CopyKitten."""

    def __init__(self):
        self._service: Optional[CopyKittenService] = None
        self._initialize_service()

    def _initialize_service(self) -> None:
        """Initialize the CopyKitten service."""
        try:
            self._service = CopyKittenService()
            logger.info("Clipboard manager initialized successfully")
        except ClipboardUnavailableError as e:
            logger.warning("Clipboard service unavailable: %s", e)
            self._service = None

    def copy(self, text: str, silent: bool = False) -> bool:
        """
        Copy text to clipboard.

        Args:
            text: Text to copy to clipboard
            silent: If True, suppress error logging and exceptions

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._service:
            if not silent:
                logger.error("Clipboard service not available")
            return False

        try:
            return self._service.copy(text)
        except ClipboardOperationError as e:
            if not silent:
                logger.error("Clipboard copy failed: %s", e)
            return False
        except Exception as e:
            if not silent:
                logger.error("Unexpected clipboard error: %s", e)
            return False

    def is_available(self) -> bool:
        """
        Check if clipboard functionality is available.

        Returns:
            bool: True if copykitten is available and functional
        """
        return self._service is not None and self._service.is_available()

    def get_service_info(self) -> str:
        """
        Get information about the clipboard service.

        Returns:
            str: Service information string
        """
        if not self._service:
            return "Clipboard service: Not available"

        version_info = self._service.get_version_info() or "copykitten"
        return f"Clipboard service: {version_info}"

    @contextmanager
    def temporary_copy(self, text: str, silent: bool = False) -> None:
        """
        Context manager for temporary clipboard operations.
        Copies text on enter, restores original content on exit if possible.

        Args:
            text: Text to temporarily copy to clipboard
            silent: If True, suppress error logging

        Note: Restoring original content may not work on all systems
        """
        original_content = None

        try:
            original_content = self._get_current_content()

            self.copy(text, silent)
            yield

        finally:
            if original_content is not None:
                self.copy(original_content, silent=True)
            elif not silent:
                logger.debug("Could not restore original clipboard content")

    def _get_current_content(self) -> Optional[str]:
        """
        Attempt to get current clipboard content.
        This is a best-effort approach since copykitten doesn't support paste.

        Returns:
            Optional[str]: Current clipboard content or None if unavailable
        """
        return None

    def clear(self, silent: bool = False) -> bool:
        """
        Clear clipboard by copying empty string.

        Args:
            silent: If True, suppress error logging

        Returns:
            bool: True if successful
        """
        return self.copy("", silent)
