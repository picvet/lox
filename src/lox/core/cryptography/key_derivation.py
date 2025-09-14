"""Key derivation functions for password-based encryption."""

import base64
import os
from typing import Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_LENGTH = 16
KEY_LENGTH = 32
PBKDF2_ITERATIONS = 100000


def derive_key(master_password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    """
    Derive a cryptographic key from a master password using PBKDF2.

    Args:
        master_password: The user's master password
        salt: Optional salt. If None, a new salt is generated.

    Returns:
        Tuple of (key, salt) - The derived key and the salt used
    """
    if salt is None:
        salt = os.urandom(SALT_LENGTH)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )

    key_material = kdf.derive(master_password.encode())
    key = base64.urlsafe_b64encode(key_material)

    return key, salt
