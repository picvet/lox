"""CopyKitten clipboard service implementation."""

import logging
from typing import Optional

try:
    import copykitten

    COPYKITTEN_AVAILABLE = True
except ImportError:
    COPYKITTEN_AVAILABLE = False

from ..exceptions import ClipboardOperationError, ClipboardUnavailableError

logger = logging.getLogger(__name__)


class CopyKittenService:
    """Clipboard service using copykitten library."""

    def __init__(self):
        if not COPYKITTEN_AVAILABLE:
            raise ClipboardUnavailableError(
                "copykitten is not installed. "
                "Please install it with: pip install copykitten"
            )

        logger.info("CopyKitten clipboard service initialized")

    def copy(self, text: str) -> bool:
        """
        Copy text to system clipboard using copykitten.

        Args:
            text: Text to copy to clipboard

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ClipboardOperationError: If copy operation fails
        """
        try:
            copykitten.copy(text)
            logger.debug("Successfully copied text to clipboard")
            return True
        except Exception as e:
            error_msg = f"Failed to copy to clipboard: {e}"
            logger.error(error_msg)
            raise ClipboardOperationError(error_msg) from e

    def is_available(self) -> bool:
        """
        Check if copykitten is available.

        Returns:
            bool: True if copykitten is installed and available
        """
        return COPYKITTEN_AVAILABLE

    def get_version_info(self) -> Optional[str]:
        """
        Get copykitten version information if available.

        Returns:
            Optional[str]: Version information or None if not available
        """
        try:
            if hasattr(copykitten, "__version__"):
                return f"copykitten v{copykitten.__version__}"
            return "copykitten (version unknown)"
        except Exception:
            return None
