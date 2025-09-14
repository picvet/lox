from argparse import Namespace

from lox.cli.commands.base import BaseCommand
from lox.infrastructure.aws.services.dynamodb_service import DynamoDBService


class PushCommand(BaseCommand):
    """Handle 'lox push' command."""

    def execute(self, args: Namespace) -> int:
        try:
            dynamo_service = DynamoDBService()
            dynamo_service.put_item(common_name="PERCY_PASS")
            self.print_success("Vault pushed to DynamoDB successfully!")
            return 0
        except Exception as e:
            self.print_error(f"Error pushing to sync: {e}")
            return 1
