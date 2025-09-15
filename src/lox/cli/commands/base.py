import getpass
import logging
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace

logger = logging.getLogger(__name__)


class CommandError(Exception):
    """Base exception for command-related errors."""

    pass


class ValidationError(CommandError):
    """Exception raised for command validation errors."""

    pass


class BaseCommand(ABC):
    """
    Abstract base class for all CLI commands.
    """

    def __init__(self):
        self.verbose = False
        self.vault = None
        self.manager = None

    @abstractmethod
    def execute(self, args: Namespace) -> int:
        """
        Execute the command with parsed arguments.
        Returns exit code (0 for success, non-zero for failure).
        """
        pass

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments to the parser."""
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Enable verbose output"
        )

    def setup(self, args: Namespace) -> None:
        """Setup command execution environment."""
        self.verbose = args.verbose

        from lox.core.services.vault_manager import VaultManager
        from lox.core.storage.local_vault import Vault

        self.vault = Vault()
        self.manager = VaultManager(self.vault)

    def cleanup(self) -> None:
        """Cleanup resources after command execution."""
        pass

    def run(self, args: Namespace) -> int:
        """Main entry point for command execution."""
        exit_code = 1

        try:
            self.setup(args)
            exit_code = self.execute(args)

        except ValidationError as e:
            print(f"Validation error: {e}")
            exit_code = 2

        except CommandError as e:
            print(f"Command error: {e}")
            exit_code = 3

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            exit_code = 130

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()
            exit_code = 4

        finally:
            try:
                self.cleanup()
            except Exception as e:
                print(f"Cleanup failed: {e}")

        return exit_code

    def get_master_password(self, args: Namespace) -> str:
        """Get master password from args or prompt user."""
        if hasattr(args, "master_password") and args.master_password:
            return args.master_password
        return getpass.getpass("Enter master password: ")

    def require_vault_exists(self) -> None:
        """Ensure vault exists before proceeding."""
        if not self.vault.vault_exists():
            raise ValidationError("No vault exists. Please run 'lox init' first.")

    def print_success(self, message: str) -> None:
        """Print success message."""
        print(f"✓ {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        print(f"✗ {message}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        print(f"ℹ️  {message}")
