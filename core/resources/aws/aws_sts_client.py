import logging

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from core.credential_manager import CredentialManager

logger = logging.getLogger(__name__)


class AWSSTSClient:
    def __init__(self):
        self.cred_manager = CredentialManager()

    def assume_role(self, role_session_name: str = "LoxPasswordManager") -> dict:
        """
        Assume the configured IAM role and return temporary credentials.
        STS temporary credentials still expire (1 hour default).
        """
        try:
            stored_creds = self.cred_manager.get_credentials()
            if not stored_creds:
                raise NoCredentialsError(
                    "No AWS credentials configured. Run 'lox sync setup'"
                )

            role_arn = stored_creds.get("role_arn")
            region = stored_creds.get("region")

            if not role_arn:
                raise ValueError("Role ARN not found in stored credentials")

            sts_client = boto3.client("sts", region_name=region)

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
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                logger.error(
                    "Access denied. Check if the role ARN is correct and you have permission to assume it."
                )
            elif error_code == "NoSuchEntity":
                logger.error("Role not found. Check if the role ARN exists.")
            raise Exception(f"AWS STS error: {e}") from e
        except Exception as e:
            logger.error("Role assumption failed: %s", e)
            raise

    def get_dynamodb_client(self):
        """Get DynamoDB client using assumed role credentials"""
        try:
            temp_creds = self.assume_role()

            return boto3.client(
                "dynamodb",
                region_name=self.cred_manager.get_credentials().get(
                    "region",
                ),
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
