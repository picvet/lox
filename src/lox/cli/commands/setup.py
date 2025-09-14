from argparse import Namespace
from typing import Tuple

from lox.cli.commands.base import BaseCommand


class SetupCommand(BaseCommand):
    """Handle 'lox setup' command."""

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
