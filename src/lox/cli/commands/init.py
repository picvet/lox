import getpass
from argparse import ArgumentParser, Namespace

from lox.cli.commands.base import BaseCommand, ValidationError


class InitCommand(BaseCommand):
    """Handle 'lox init' command."""

    def execute(self, args: Namespace) -> int:
        if self.vault.vault_exists():
            self.print_error(
                "Vault already exists. Use 'lox reset' to create a new vault."
            )
            return 1

        print("Initializing new Lox password vault...")
        print(
            "⚠️  Warning: If you forget this password, you'll lose access to your stored credentials."
        )
        print()

        while True:
            master_password = getpass.getpass("Enter master password: ")
            if not master_password.strip():
                print("Password cannot be empty. Please try again.")
                continue

            confirm_password = getpass.getpass("Confirm master password: ")

            if master_password == confirm_password:
                break
            else:
                print("Passwords do not match. Please try again.")
                print()

        if self.vault.initialize_vault(master_password):
            self.print_success("Vault created successfully!")
            print("You can now add credentials using 'lox add' command.")
            return 0
        else:
            self.print_error("Failed to create vault. Please try again.")
            return 1
