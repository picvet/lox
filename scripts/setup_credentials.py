"""Interactive AWS credentials setup for Lox Password Manager."""

import logging
from typing import Tuple

from core.credential_manager import CredentialManager
from core.utils.validation import (validate_aws_access_key,
                                   validate_aws_region, validate_aws_role_arn,
                                   validate_aws_secret_key)

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

        role_arn, access_key, secret_key, region = _prompt_for_credentials()

        if not validate_aws_role_arn(role_arn):
            raise CredentialSetupError("Invalid AWS role arn provided!")
        if not validate_aws_region(region):
            raise CredentialSetupError("Invalid DynamoDB regoin provided!")
        if not validate_aws_secret_key(secret_key):
            raise CredentialSetupError("Invalid AWS secret key!")
        if not validate_aws_access_key(access_key):
            raise CredentialSetupError("Invalid AWS access key provided!")

        credential_manager = CredentialManager()

        if credential_manager.store_credentials(
            role_arn,
            access_key,
            secret_key,
            region,
        ):
            print("✅ Credentials stored securely!")
        else:
            raise CredentialSetupError("Failed to store credentials securely")

    except (EOFError, KeyboardInterrupt):
        print("\n\nSetup cancelled by user.")
        raise CredentialSetupError("Setup cancelled") from None
    except Exception as e:
        logger.error("Credential setup failed: %s", e)
        raise CredentialSetupError(f"Setup failed: {e}") from e


def _prompt_for_credentials() -> Tuple[
    str,
    str,
    str,
]:
    """Prompt user for AWS credentials with input validation."""
    try:
        role_arn = input("Enter role arn: ").strip()
        if not role_arn:
            raise ValueError("Role arn cannot be empty")

        access_key = input("Enter access key: ").strip()
        if not access_key:
            raise ValueError("Access key cannot be empty")

        secret_key = input("Enter secret key: ").strip()
        if not secret_key:
            raise ValueError("Secret key cannot be empty")

        region = input("Enter region of DynamoDB: ").strip()
        if not region:
            raise ValueError("DynamoDB region cannot be empty")

        return role_arn, access_key, secret_key, region

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
