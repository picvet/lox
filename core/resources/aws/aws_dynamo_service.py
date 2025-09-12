import base64
import logging
import time
import uuid

from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

from core.resources.aws.aws_sts_client import AWSSTSClient
from core.storage import Vault

logger = logging.getLogger(__name__)
deserializer = TypeDeserializer()


class DynamoDBService:
    """
    Service class to perform common DynamoDB operations.
    It uses the AWSSTSClient to handle authentication.
    """

    def __init__(self):
        self.sts_client = AWSSTSClient()
        self.table_name = "loxpasswordmanager"

    def put_item(
        self,
        common_name: str,
    ) -> bool:
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
            current_time_ms = str(int(time.time() * 1000))

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
                "pk": {"S": "VAULT_DATA"},
                "sk": {"S": unique_id},  # The unique ID is now the sort key
                "common_name": {"S": common_name},
                "timestamp_ms": {"N": current_time_ms},
                "vault_data": {"S": string_vault_data},
                "record_type": {"S": "DATA_VAULT"},
            }

            response = dynamoDB.put_item(
                TableName=self.table_name,
                Item=item,
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info(
                    f"Successfully uploaded item to table {
                        self.table_name}"
                )
                print(f"Successfully uploaded item to table {self.table_name}")
                return True
            else:
                print("Status not 200")
                logger.info(f"Failed to upload item. Response {response}")
                return False

        except ClientError as e:
            logger.error(
                f"ClientError when uploading item: {
                    e.response['Error']}"
            )
            return False
        except Exception as e:
            logger.error(f"Unexpected error when uploading item: {e}")
            return False

    def get_last_item_query(self):
        try:
            dynamoDB = self.sts_client.get_dynamodb_resource()
            table = dynamoDB.Table(self.table_name)

            # The KeyConditionExpression must reference the GSI's Partition Key
            response = table.query(
                IndexName="TimestampIndex",
                KeyConditionExpression=Key("record_type").eq("DATA_VAULT"),
                ScanIndexForward=False,
                Limit=1,
            )

            items = response.get("Items", [])
            if not items:
                print("No items found.")
                return None

            # The boto3 resource API handles deserialization automatically,
            # so you don't need the deserializer logic.
            last_item = items[0]
            return last_item

        except Exception as e:
            print(f"Error retrieving last item: {e}")
            return None
