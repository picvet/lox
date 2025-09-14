import os
from argparse import ArgumentParser, Namespace

from lox.cli.commands.base import BaseCommand, ValidationError


class ResetCommand(BaseCommand):
    """Handle 'lox reset' command."""

    def execute(self, args: Namespace) -> int:
        if not self.vault.vault_exists():
            self.print_error("No vault exists. Use 'lox init' to create one.")
            return 1

        print("⚠️  WARNING: This will delete ALL stored credentials!")
        print("You will lose access to all passwords permanently.")
        print()

        confirmation = input("Are you sure you want to reset the vault? (y/n): ")

        if confirmation.lower() not in ["y", "yes"]:
            print("Reset cancelled.")
            return 0

        try:
            os.remove(self.vault.vault_path)
            self.print_success("Vault deleted.")
            print()

            from lox.cli.commands.init import InitCommand

            init_cmd = InitCommand()
            return init_cmd.run(args)

        except Exception as e:
            self.print_error(f"Error resetting vault: {e}")
