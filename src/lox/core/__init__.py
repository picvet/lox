"""Core functionality for Lox password manager."""

from .cryptography import decrypt_data, derive_key, encrypt_data
from .exceptions import (ConfigurationError, DecryptionError, EncryptionError,
                         LoxError, PasswordGenerationError, SecurityError,
                         ValidationError, VaultError, VaultNotFoundError,
                         VaultOperationError)
from .services import VaultManager, generate_password
from .storage import Vault

__all__ = [
    "derive_key",
    "encrypt_data",
    "decrypt_data",
    "generate_password",
    "VaultManager",
    "LoxError",
    "VaultError",
    "VaultNotFoundError",
    "VaultOperationError",
    "EncryptionError",
    "DecryptionError",
    "PasswordGenerationError",
    "ValidationError",
    "SecurityError",
    "ConfigurationError",
    "Vault",
]
