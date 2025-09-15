"""DynamoDB service for vault synchronization."""

import base64
import logging
import time
import uuid
from typing import Optional

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from lox.core.storage.local_vault import Vault
from lox.infrastructure.aws.services.sts_service import STSService

logger = logging.getLogger(__name__)


class DynamoDBServiceError(Exception):
    """Exception for DynamoDB service errors."""

    pass


class DynamoDBService:
    """Service for DynamoDB vault synchronization operations."""

    def __init__(
        self,
        table_name: str = "loxpasswordmanager",
        sts_service: Optional[STSService] = None,
    ):
        self.table_name = table_name
        self.sts_service = sts_service or STSService()

    def upload_vault(self, common_name: str) -> bool:
        """
        Upload encrypted vault to DynamoDB.

        Args:
            common_name: Identifier for the vault

        Returns:
            bool: True if upload successful

        Raises:
            DynamoDBServiceError: If upload fails
        """
        try:
            vault = Vault()
            vault_bytes = vault.get_encrypted_vault()
            base64_vault_data = base64.b64encode(vault_bytes).decode("ascii")

            item = {
                "pk": {"S": "VAULT_DATA"},
                "sk": {"S": str(uuid.uuid4())},
                "common_name": {"S": common_name},
                "timestamp_ms": {"N": str(int(time.time() * 1000))},
                "vault_data": {"S": base64_vault_data},
                "record_type": {"S": "DATA_VAULT"},
            }

            dynamodb = self.sts_service.get_client_with_assumed_role("dynamodb")
            response = dynamodb.put_item(
                TableName=self.table_name,
                Item=item,
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info("Successfully uploaded vault to DynamoDB")
                return True
            else:
                logger.error("Failed to upload vault. Response: %s", response)
                return False

        except ClientError as e:
            error_msg = f"DynamoDB upload failed: {e.response['Error']}"
            logger.error(error_msg)
            raise DynamoDBServiceError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during upload: {e}"
            logger.error(error_msg)
            raise DynamoDBServiceError(error_msg) from e

    def download_latest_vault(self) -> bool:
        """
        Download and sync the latest vault from DynamoDB.

        Returns:
            bool: True if download and sync successful

        Raises:
            DynamoDBServiceError: If download fails
        """
        try:
            dynamodb = self.sts_service.get_resource_with_assumed_role("dynamodb")
            table = dynamodb.Table(self.table_name)

            response = table.query(
                IndexName="TimestampIndex",
                KeyConditionExpression=Key("record_type").eq("DATA_VAULT"),
                ScanIndexForward=False,
                Limit=1,
            )

            items = response.get("Items", [])
            if not items:
                logger.warning("No vaults found in DynamoDB")
                return False

            # Extract and decode vault data
            vault_data = items[0].get("vault_data")
            if not vault_data:
                logger.error("No vault data found in DynamoDB item")
                return False

            cloud_bytes = base64.b64decode(vault_data.encode("ascii"))

            # Sync with local vault
            vault = Vault()
            success = vault.sync_replace_local_file_content(cloud_bytes)

            if success:
                logger.info("Successfully synced vault from cloud")
                return True
            else:
                logger.error("Failed to sync vault from cloud")
                return False

        except ClientError as e:
            error_msg = f"DynamoDB download failed: {e.response['Error']}"
            logger.error(error_msg)
            raise DynamoDBServiceError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during download: {e}"
            logger.error(error_msg)
            raise DynamoDBServiceError(error_msg) from e

    def list_vaults(self) -> Optional[list]:
        """
        List all vaults in DynamoDB.

        Returns:
            Optional[list]: List of vault metadata or None if failed
        """
        try:
            dynamodb = self.sts_service.get_resource_with_assumed_role("dynamodb")
            table = dynamodb.Table(self.table_name)

            response = table.query(
                IndexName="TimestampIndex",
                KeyConditionExpression=Key("record_type").eq("DATA_VAULT"),
                ScanIndexForward=False,
            )

            vaults = []
            for item in response.get("Items", []):
                vaults.append(
                    {
                        "common_name": item.get("common_name"),
                        "timestamp": item.get("timestamp_ms"),
                        "record_id": item.get("sk"),
                    }
                )

            return vaults

        except Exception as e:
            logger.error("Failed to list vaults: %s", e)
            return None
