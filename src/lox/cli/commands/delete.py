from argparse import ArgumentParser, Namespace

from lox.cli.commands.base import BaseCommand, ValidationError


class DeleteCommand(BaseCommand):
    """Handle 'lox delete' command."""

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

        confirmation = input(f"Are you sure you want to delete {name}? (y/n): ")

        if confirmation.lower() not in ["y", "yes"]:
            print("Delete cancelled.")
            return 0

        del vault_data["services"][name]

        if self.manager.save_vault_data(vault_data, master_password):
            self.print_success(f"Password for '{name}' deleted.")
            return 0
        else:
            self.print_error(f"Failed to delete password for '{name}'.")
            return 1
