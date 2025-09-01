import copykitten


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard.

    Args:
        text (str): Text to copy to clipboard.

    Returns:
        bool: True if successul, False otherwise.
    """
    try:
        copykitten.copy(text)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False
