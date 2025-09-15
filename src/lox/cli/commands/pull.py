from argparse import Namespace

from lox.cli.commands.base import BaseCommand
from lox.infrastructure.aws.services.dynamodb_service import DynamoDBService


class PullCommand(BaseCommand):
    """Handle 'lox pull' command."""

    def execute(self, args: Namespace) -> int:
        try:
            dynamo_service = DynamoDBService()
            dynamo_service.download_latest_vault()
            self.print_success("Vault pulled from DynamoDB successfully!")
            return 0
        except Exception as e:
            self.print_error(f"Error pulling from sync: {e}")
            return 1
