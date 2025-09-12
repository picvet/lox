import base64
import logging
import uuid

from botocore.exceptions import ClientError

from core.resources.aws.aws_sts_client import AWSSTSClient
from core.storage import Vault

logger = logging.getLogger(__name__)


class DynamoDBService:
    """
    Service class to perform common DynamoDB operations.
    It uses the AWSSTSClient to handle authentication.
    """

    def __init__(self):
        self.sts_client = AWSSTSClient()

    def put_item(self, table_name: str = "loxpasswordmanager") -> bool:
        """
        Uploads a new item to a DynamoDB table.

        Args:
            table_name (str): The name of the DynamoDB table.
            item (Dict[str, Any]): The item to be uploaded. The item
                must be formatted with DynamoDB's data types'

        Returns:
            bool: True if the item was uploaded successfully, False otherwise.
        """

        try:
            unique_id = str(uuid.uuid4())

            vault_bytes = Vault().get_encrypted_vault()

            base64_encoded_vault_bytes = base64.b64encode(vault_bytes)
            string_vault_data = base64_encoded_vault_bytes.decode("ascii")

            dynamoDB = self.sts_client.get_dynamodb_client()

            # base64_encoded_vault_bytes = base64.b64encode(vault_bytes)
            #
            # string_vault_data = base64_encoded_vault_bytes.decode("ascii")
            #
            # base64_encoded_bytes = string_vault_data.encode("ascii")
            #
            # original_vault_bytes = base64.b64decode(base64_encoded_bytes)
            #
            # b_equal = original_vault_bytes == vault_bytes
            # if b_equal:
            #     print("Bytes are equal")

            item = {
                "lox_credential_id": {"S": unique_id},
                "vault_data": {"S": string_vault_data},
            }

            print("Before response")
            response = dynamoDB.put_item(
                TableName=table_name,
                Item=item,
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info(f"Successfully uploaded item to table {table_name}")
                print(f"Successfully uploaded item to table {table_name}")
                return True
            else:
                print("Status not 200")
                logger.info(f"Failed to upload item. Response {response}")
                return False

        except ClientError as e:
            print(f"Client Error: {e}")
            logger.error(
                f"ClientError when uploading item: {
                    e.response['Error']}"
            )
            return False
        except Exception as e:
            print(f"Exception Error: {e}")
            logger.error(f"Unexpected error when uploading item: {e}")
            return False
