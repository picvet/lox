from argparse import ArgumentParser, Namespace

from lox.cli.commands.base import BaseCommand
from lox.infrastructure.clipboard.services.manager import ClipboardManager


class GetCommand(BaseCommand):
    """Handle 'lox get' command."""

    def add_arguments(self, parser: ArgumentParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--name", "-n", required=True, help="Name of the application"
        )

    def execute(self, args: Namespace) -> int:
        self.require_vault_exists()

        master_password = self.get_master_password(args)

        try:
            vault_data = self.manager.get_vault_data(master_password)
        except (FileNotFoundError, ValueError) as e:
            self.print_error(str(e))
            return 1

        name = args.name

        if name not in vault_data["services"]:
            self.print_error(f"'{name}' not found in the vault.")
            return 1

        password = vault_data["services"][name]["password"]
        print(f"Password for '{name}': {password}")

        clipboard = ClipboardManager()

        if clipboard.copy(password):
            self.print_success("Copied to clipboard!")
        else:
            self.print_error("Failed to copy to clipboard.")

        return 0
