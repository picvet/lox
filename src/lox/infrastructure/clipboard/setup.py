"""Clipboard setup and verification utilities."""

import logging
from typing import Any, Dict

from . import copy_to_clipboard, get_clipboard_info, is_clipboard_available

logger = logging.getLogger(__name__)


def verify_clipboard_setup() -> Dict[str, Any]:
    """
    Verify that clipboard functionality is properly set up.

    Returns:
        Dict containing setup verification results

    Example:
        >>> verify_clipboard_setup()
        {
            'available': True,
            'info': 'copykitten v1.2.3',
            'test_successful': True,
            'test_message': 'Clipboard test passed'
        }
    """
    results = {
        "available": False,
        "info": "",
        "test_successful": False,
        "test_message": "",
    }

    try:
        results["available"] = is_clipboard_available()
        results["info"] = get_clipboard_info()

        if not results["available"]:
            results["test_message"] = "Clipboard not available"
            return results

        test_text = "Lox clipboard test 123"
        success = copy_to_clipboard(test_text, silent=True)

        if success:
            results["test_successful"] = True
            results["test_message"] = "Clipboard test passed"
        else:
            results["test_message"] = "Clipboard test failed"

        return results

    except Exception as e:
        results["test_message"] = f"Setup verification failed: {e}"
        return results


def print_clipboard_status() -> None:
    """Print clipboard status information to console."""
    status = verify_clipboard_setup()

    print("📋 Clipboard Status")
    print("=" * 50)
    print(f"Available: {'✅ Yes' if status['available'] else '❌ No'}")
    print(f"Service: {status['info']}")
    print(
        f"Test: {'✅ ' + status['test_message']
                 if status['test_successful'] else '❌ ' + status['test_message']}"
    )
    if not status["available"]:
        print("\n💡 To enable clipboard  functionality:")
        print("   pip install copykitten")
