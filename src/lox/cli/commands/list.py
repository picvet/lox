from argparse import ArgumentParser, Namespace

from lox.cli.commands.base import BaseCommand, ValidationError


class ListCommand(BaseCommand):
    """Handle 'lox list' command."""

    def execute(self, args: Namespace) -> int:
        self.require_vault_exists()

        master_password = self.get_master_password(args)

        try:
            vault_data = self.manager.get_vault_data(master_password)
        except (FileNotFoundError, ValueError) as e:
            self.print_error(str(e))
            return 1

        services = vault_data.get("services", {})

        if not services:
            print("No services stored in the vault.")
            return 0

        print("Stored services:")
        for name in services.keys():
            print(f"- {name}")
