"""Interactive AWS credentials setup for Lox Password Manager."""

import logging
from typing import Optional, Tuple

from core.credential_manager import CredentialManager
from core.utils.validation import validate_aws_credentials

logger = logging.getLogger(__name__)


class CredentialSetupError(Exception):
    """Custom exception for credential setup failures."""

    pass


def setup_aws_credentials() -> None:
    """
    Interactive AWS credentials setup with validation and secure storage.

    Raises:
        CredentialSetupError: If credential setup fails
    """
    try:
        print("🔐 AWS Credentials Setup for Lox Password Manager")
        print("=" * 50)

        # Get credentials with validation
        credentials = _prompt_for_credentials()

        # Validate before storing
        if not validate_aws_credentials(credentials[0], credentials[1]):
            raise CredentialSetupError("Invalid AWS credentials provided")

        # Store securely
        credential_manager = CredentialManager()
        expiry_days = 30

        if credential_manager.store_credentials(*credentials, expiry_days):
            print("✅ Credentials stored securely!")
            print(f"\nNext steps:")
            print("1. Run 'lox sync test' to verify connection")
            print(f"2. Credentials will be valid for {expiry_days} days")
        else:
            raise CredentialSetupError("Failed to store credentials securely")

    except (EOFError, KeyboardInterrupt):
        print("\n\nSetup cancelled by user.")
        raise CredentialSetupError("Setup cancelled") from None
    except Exception as e:
        logger.error("Credential setup failed: %s", e)
        raise CredentialSetupError(f"Setup failed: {e}") from e


def _prompt_for_credentials() -> Tuple[str, str, str]:
    """Prompt user for AWS credentials with input validation."""
    try:
        aws_access_key = input("Enter AWS Access Key ID: ").strip()
        if not aws_access_key:
            raise ValueError("Access Key ID cannot be empty")

        aws_secret_key = input("Enter AWS Secret Access Key: ").strip()
        if not aws_secret_key:
            raise ValueError("Secret Access Key cannot be empty")

        region = input("Enter AWS Region (default: us-east-1): ").strip()
        region = region or "us-east-1"

        return aws_access_key, aws_secret_key, region

    except ValueError as e:
        print(f"❌ Validation error: {e}")
        raise


def store_credentials_securely(
    access_key: str,
    secret_key: str,
    region: str,
) -> bool:
    """
    Store credentials using platform-specific secure storage.

    Args:
        access_key: AWS Access Key ID
        secret_key: AWS Secret Access Key
        region: AWS region

    Returns:
        bool: True if storage successful, Falase otherwise
    """
    try:
        credential_manager = CredentialManager()
        return credential_manager.store_credentials(access_key, secret_key, region)
    except Exception as e:
        logger.warning("Secure storage failed: %s", e)
        return False
