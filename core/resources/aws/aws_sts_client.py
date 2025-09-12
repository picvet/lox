import logging
from typing import Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from core.credential_manager import CredentialManager

logger = logging.getLogger(__name__)


class AWSSTSClient:
    def __init__(self):
        self.cred_manager = CredentialManager()
        self.region = "eu-north-1"

    def assume_role(self) -> Dict[str, str]:
        """
        Assume the configured IAM role and return temporary credentials.
        STS temporary credentials still expire (1 hour default).
        """
        role_session_name = "LoxPasswordManager"
        stored_creds = self.cred_manager.get_credentials()

        if not stored_creds:
            raise NoCredentialsError(
                "No AWS credentials configured. Run 'lox sync setup'"
            )

        role_arn = stored_creds.get("role_arn")
        access_key = stored_creds.get("access_key")
        secret_key = stored_creds.get("secret_key")

        if not role_arn:
            raise ValueError("Role ARN not found in stored credentials")
        if not access_key:
            raise ValueError("Access key not found in stored credentials")
        if not secret_key:
            raise ValueError("Secret key not found in stored credentials")

        try:
            sts_client = boto3.client(
                "sts",
                region_name=self.region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )

            response = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=role_session_name,
                DurationSeconds=3600,
            )

            creds = response["Credentials"]
            return {
                "access_key": creds["AccessKeyId"],
                "secret_key": creds["SecretAccessKey"],
                "session_token": creds["SessionToken"],
                "expiration": creds["Expiration"].isoformat(),
                "region": self.region,
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                logger.error("Access denied for role ARN '%s'.", role_arn)
            elif error_code == "NoSuchEntity":
                logger.error("Role ARN '%s' does not exist.", role_arn)
            else:
                logger.error("AWS STS client error: %s", e)
            raise RuntimeError(f"AWS STS error: {e}") from e

        except BotoCoreError as e:
            logger.error("Low-level boto3 error: %s", e)
            raise RuntimeError("Failed to communicate with AWS STS") from e

    def get_dynamodb_client(self):
        """Get DynamoDB client using assumed role credentials"""
        try:
            temp_creds = self.assume_role()

            return boto3.client(
                "dynamodb",
                region_name=self.region,
                aws_access_key_id=temp_creds["access_key"],
                aws_secret_access_key=temp_creds["secret_key"],
                aws_session_token=temp_creds["session_token"],
            )
        except Exception as e:
            logger.error("Failed to create DynamoDB client: %s", e)
            raise

    def are_credentials_configured(self) -> bool:
        """Check if credentials are configured (no expiry check)"""
        return self.cred_manager.are_credentials_configured()
