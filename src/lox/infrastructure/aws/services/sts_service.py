"""AWS STS service for role assumption."""

import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from lox.infrastructure.aws.models.credentials import AWSCredentials
from lox.infrastructure.aws.services.credential_service import \
    AWSCredentialService

logger = logging.getLogger(__name__)


class STSAssumptionError(Exception):
    """Exception for STS role assumption failures."""

    pass


class STSService:
    """Service for AWS STS operations."""

    def __init__(
        self,
        credential_service: Optional[AWSCredentialService] = None,
    ):
        self.credential_service = credential_service or AWSCredentialService()

    def assume_role(
        self, role_session_name: str = "LoxPasswordManager"
    ) -> AWSCredentials:
        """
        Assume the configured IAM role and return temporary credentials.

        Returns:
            AWSCredentials: Temporary credentials including session token

        Raises:
            STSAssumptionError: If role assumption fails
        """
        stored_data = self.credential_service.retrieve_credentials()
        if not stored_data:
            raise NoCredentialsError("No AWS credentials configured. Run 'lox setup'")

        stored_creds = AWSCredentials.from_dict(stored_data)

        if not stored_creds.are_complete():
            raise ValueError("Incomplete AWS credentials stored")

        try:
            sts_client = boto3.client(
                "sts",
                region_name=stored_creds.region,
                aws_access_key_id=stored_creds.access_key,
                aws_secret_access_key=stored_creds.secret_key,
            )

            # Assume the role
            response = sts_client.assume_role(
                RoleArn=stored_creds.role_arn,
                RoleSessionName=role_session_name,
                DurationSeconds=3600,  # 1 hour session
            )

            creds = response["Credentials"]
            return AWSCredentials(
                access_key=creds["AccessKeyId"],
                secret_key=creds["SecretAccessKey"],
                session_token=creds["SessionToken"],
                region=stored_creds.region,
            )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = self._get_error_message(error_code, stored_creds.role_arn)
            logger.error(error_message)
            raise STSAssumptionError(error_message) from e

        except Exception as e:
            logger.error("STS assumption failed: %s", e)
            raise STSAssumptionError(f"STS assumption failed: {e}") from e

    def _get_error_message(self, error_code: str, role_arn: str) -> str:
        """Get user-friendly error message for STS errors."""
        error_messages = {
            "AccessDenied": f"Access denied for role '{role_arn}'. Check permissions.",
            "NoSuchEntity": f"Role '{role_arn}' does not exist.",
            "ExpiredToken": "Credentials have expired. Please run 'lox setup' again.",
            "InvalidClientTokenId": "Invalid access key. Please run 'lox setup' again.",
        }
        return error_messages.get(error_code, f"AWS error: {error_code}")

    def get_client_with_assumed_role(self, service_name: str, **kwargs):
        """
        Get a boto3 client with assumed role credentials.

        Args:
            service_name: Name of the AWS service
            **kwargs: Additional client configuration

        Returns:
            boto3 client configured with assumed role credentials
        """
        temp_creds = self.assume_role()

        return boto3.client(
            service_name,
            region_name=temp_creds.region,
            aws_access_key_id=temp_creds.access_key,
            aws_secret_access_key=temp_creds.secret_key,
            aws_session_token=temp_creds.session_token,
            **kwargs,
        )

    def get_resource_with_assumed_role(self, service_name: str, **kwargs):
        """
        Get a boto3 resource with assumed role credentials.

        Args:
            service_name: Name of the AWS service
            **kwargs: Additional resource configuration

        Returns:
            boto3 resource configured with assumed role credentials
        """
        temp_creds = self.assume_role()

        return boto3.resource(
            service_name,
            region_name=temp_creds.region,
            aws_access_key_id=temp_creds.access_key,
            aws_secret_access_key=temp_creds.secret_key,
            aws_session_token=temp_creds.session_token,
            **kwargs,
        )
