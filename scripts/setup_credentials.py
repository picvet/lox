"""Interactive AWS credentials setup for Lox Password Manager."""

import logging
from typing import Tuple

from core.credential_manager import CredentialManager
from core.utils.validation import validate_aws_role_arn

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

        credentials = _prompt_for_credentials()

        if not validate_aws_role_arn(credentials[0]):
            raise CredentialSetupError("Invalid AWS role arn provided!")

        credential_manager = CredentialManager()

        if credential_manager.store_credentials(*credentials):
            print("✅ Credentials stored securely!")
            print(f"\nNext steps:")
            print("1. Run 'lox sync test' to verify connection")
        else:
            raise CredentialSetupError("Failed to store credentials securely")

    except (EOFError, KeyboardInterrupt):
        print("\n\nSetup cancelled by user.")
        raise CredentialSetupError("Setup cancelled") from None
    except Exception as e:
        logger.error("Credential setup failed: %s", e)
        raise CredentialSetupError(f"Setup failed: {e}") from e


def _prompt_for_credentials() -> Tuple[str, str]:
    """Prompt user for AWS credentials with input validation."""
    try:
        role_arn = input("Enter role arn: ").strip()
        if not role_arn:
            raise ValueError("Role arn cannot be empty")

        region = input("Enter AWS Region name: ").strip()
        region = region or "us-east-1"

        return role_arn, region

    except ValueError as e:
        print(f"❌ Validation error: {e}")
        raise


def store_credentials_securely(
    role_arn: str,
    region: str,
) -> bool:
    """
    Store credentials using platform-specific secure storage.

    Args:
        role_arn: AWS role arn
        region: AWS region

    Returns:
        bool: True if storage successful, Falase otherwise
    """
    try:
        credential_manager = CredentialManager()
        return credential_manager.store_credentials(role_arn, region)
    except Exception as e:
        logger.warning("Secure storage failed: %s", e)
        return False
