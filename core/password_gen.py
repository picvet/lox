import secrets
import string


def generate_password(
    length=12,
    use_symbol=True,
    use_digits=True,
    use_uppercase=True,
) -> str:
    """
    Generate a string random password.

    Args:
        length (int): Length of the passsword. Defaults to 12.
        use_symbol (bool): Include symbols. Defaults to True.
        use_digits (bool): Includes digits. Defaults to True.
        use_uppercase (bool): Include uppercase letters. Defaults to
        True.

    Returns:
        str: The generated password.

    Raises:
        ValueError: If no character sets are selected or length is too
        small.
    """

    # define character sets
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase if use_uppercase else ""
    digits = string.digits if use_digits else ""
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if use_symbol else ""

    # combine all allowed character sets
    all_chars = lowercase_letters + uppercase_letters + digits + symbols

    if not all_chars or (not use_symbol and not use_digits and not use_uppercase):
        raise ValueError(
            "At least one character set must be enabled."
            "\nAvailable sets: lowercase letters, uppercase letters, digits, symbols."
            "\nYou've disabled all optional sets (uppercase, digits, symbols),"
        )

    if length < 7:
        raise ValueError("Password length must be at least 8 characters")

    password = "".join(secrets.choice(all_chars) for _ in range(length))

    return password


# This is a very long comment that should definetely exceed eight-ychatacters and should
# be automatically wrapped by formatter


def very_long_function_name_with_many_characters(
    parameter1: str, parameter2: str, parameter3: str, parameter4: str
):
    return "this is a very long string that might also need to be wrapped properly"
