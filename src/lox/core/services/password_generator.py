"""Password generation service."""

import secrets
import string

from ..exceptions import PasswordGenerationError


def generate_password(
    length: int = 16,
    use_symbols: bool = True,
    use_digits: bool = True,
    use_uppercase: bool = True,
    exclude_similar: bool = True,
) -> str:
    """
    Generate a secure random password.

    Args:
        length: Length of the password (default: 16)
        use_symbols: Include symbols (default: True)
        use_digits: Include digits (default: True)
        use_uppercase: Include uppercase letters (default: True)
        exclude_similar: Exclude similar characters like 1lI0O (default: True)

    Returns:
        Generated password string

    Raises:
        PasswordGenerationError: If no character sets are selected or length is invalid
    """
    lowercase_letters = string.ascii_lowercase

    uppercase_letters = string.ascii_uppercase if use_uppercase else ""
    if exclude_similar and use_uppercase:
        uppercase_letters = "".join(c for c in uppercase_letters if c not in "IO")

    digits = string.digits if use_digits else ""
    if exclude_similar and use_digits:
        digits = "".join(c for c in digits if c not in "01")

    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if use_symbols else ""

    all_chars = lowercase_letters + uppercase_letters + digits + symbols

    if not all_chars:
        raise PasswordGenerationError(
            "At least one character set must be enabled. "
            "Available sets: lowercase letters, uppercase letters, digits, symbols."
        )

    if length < 8:
        raise PasswordGenerationError("Password length must be at least 8 characters")

    if length > 128:
        raise PasswordGenerationError("Password length cannot exceed 128 characters")

    try:
        password = "".join(secrets.choice(all_chars) for _ in range(length))
        return password
    except Exception as e:
        raise PasswordGenerationError(f"Failed to generate password: {e}") from e
