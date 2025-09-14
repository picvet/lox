"""Core exceptions for Lox password manager."""


class LoxError(Exception):
    """Base exception for all Lox errors."""

    pass


class VaultError(LoxError):
    """Base exception for vault-related errors."""

    pass


class VaultNotFoundError(VaultError):
    """Exception raised when vault file doesn't exist."""

    pass


class VaultOperationError(VaultError):
    """Exception raised when vault operations fail."""

    pass


class EncryptionError(LoxError):
    """Exception raised when encryption fails."""

    pass


class DecryptionError(LoxError):
    """Exception raised when decryption fails."""

    pass


class PasswordGenerationError(LoxError):
    """Exception raised when password generation fails."""

    pass


class ValidationError(LoxError):
    """Exception raised when validation fails."""

    pass


class ConfigurationError(LoxError):
    """Exception raised when configuration is invalid."""

    pass


class SecurityError(LoxError):
    """Exception raised for security-related issues."""

    pass
