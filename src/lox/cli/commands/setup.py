import logging
from argparse import Namespace
from typing import Tuple

from lox.cli.commands.base import BaseCommand
from lox.infrastructure.aws import CredentialSetupError
from lox.infrastructure.aws.services.credential_service import \
    AWSCredentialService
from lox.infrastructure.aws.utils.validation import validate_aws_credentials

logger = logging.getLogger(__name__)


class SetupCommand(BaseCommand):
    """Handle 'lox setup' command."""

    def execute(self):
        try:
            print("🔐 AWS Credentials Setup for Lox Password Manager")
            print("=" * 50)

            aws_credential_service = AWSCredentialService()

            aws_credentials = aws_credential_service.prompt_for_credentials()

            validation_error = validate_aws_credentials(aws_credentials)

            if validation_error:
                print(f"Validation failed: {validation_error}")
                raise CredentialSetupError(
                    f"AWS credential validation failed: {validation_error}"
                )

            if aws_credential_service.store_credentials(aws_credentials):
                print("Credentials stored securely!")
            else:
                raise CredentialSetupError("Failed to store credentials securely")

        except (EOFError, KeyboardInterrupt):
            print("\n\nSetup cancelled by user.")
            raise CredentialSetupError("Setup cancelled") from None
        except CredentialSetupError as e:
            logger.error("Credential setup error: %s", e)
            raise e
        except Exception as e:
            logger.error("Credential setup failed: %s", e)
            raise CredentialSetupError(f"Setup failed: {e}") from e
