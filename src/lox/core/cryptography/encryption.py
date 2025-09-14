"""Encryption and decryption functions using Fernet."""

from typing import Union

from cryptography.fernet import Fernet, InvalidToken

from ..exceptions import DecryptionError, EncryptionError


def encrypt_data(data: Union[str, bytes], key: bytes) -> bytes:
    """
    Encrypt data using the derived key.

    Args:
        data: The data to encrypt (string or bytes)
        key: The encryption key

    Returns:
        Encrypted data as bytes

    Raises:
        EncryptionError: If encryption fails
    """
    try:
        if isinstance(data, str):
            data = data.encode("utf-8")

        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        return encrypted_data

    except Exception as e:
        raise EncryptionError(f"Encryption failed: {e}") from e


def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    """
    Decrypt data using the derived key.

    Args:
        encrypted_data: The encrypted data
        key: The encryption key

    Returns:
        Decrypted data as string

    Raises:
        DecryptionError: If decryption fails or authentication fails
    """
    try:
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data.decode("utf-8")

    except InvalidToken:
        raise DecryptionError("Decryption failed: Invalid token or corrupted data")
    except Exception as e:
        raise DecryptionError(f"Decryption failed: {e}") from e
