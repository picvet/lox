import base64
import os
from typing import Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_LENGTH = 16
KEY_LENGTH = 32
PBKDF2_ITERATIONS = 100000


def derive_key(
    master_password: str,
    salt: bytes = None,
) -> Tuple[bytes, bytes]:
    """
    Derive a cryptographic key from a master password using PBKDF2.

    Args:
        master_password (str): The user's master password
        salt (bytes): Optional salt. If None, a new salt is generated.

    Returns:
        Tuple[bytes, bytes]: (key, salt) - The derived key and the salt used
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


def encrypt_data(
    data: str,
    key: bytes,
) -> bytes:
    """
    Encrypt data using the derived key.

    Args:
        data (str): The data to encrypt (usually JSON string)
        key (bytes): The encryption key

    Returns:
        bytes: Encrypted data
    """
    try:
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data
    except Exception as e:
        raise ValueError(f"Encryption failed: {e}")


def decrypt_data(
    encrypted_data: bytes,
    key: bytes,
) -> str:
    """
    Decrypt data using the derived key.

    Args:
        encrypted_data (bytes): The encrypted data
        key (bytes): The encryption key

    Returns:
        str: Decrypted data
    """
    try:
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")
