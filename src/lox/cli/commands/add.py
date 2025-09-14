from argparse import ArgumentParser, Namespace

from lox.cli.commands.base import BaseCommand
from lox.core.services.password_generator import generate_password
from lox.infrastructure.clipboard.services.manager import ClipboardManager


class AddCommand(BaseCommand):
    """Handle 'lox add' command."""

    def add_arguments(self, parser: ArgumentParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--name", "-n", help="Name of the application for this password"
        )
        parser.add_argument(
            "--length",
            "-l",
            type=int,
            default=16,
            help="Length of the password (default: 16)",
        )
        parser.add_argument(
            "--no-symbols",
            "-ns",
            action="store_false",
            dest="symbols",
            help="Exclude symbols from the password",
        )
        parser.add_argument(
            "--no-digits",
            "-nd",
            action="store_false",
            dest="digits",
            help="Exclude digits from the password",
        )
        parser.add_argument(
            "--no-uppercase",
            "-nu",
            action="store_false",
            dest="uppercase",
            help="Exclude uppercase letters from the password",
        )

    def execute(self, args: Namespace) -> int:
        self.require_vault_exists()

        master_password = self.get_master_password(args)

        try:
            vault_data = self.manager.get_vault_data(master_password)
        except (FileNotFoundError, ValueError) as e:
            self.print_error(str(e))
            return 1

        # Get application name
        if not args.name:
            while True:
                name = input("Enter name of application: ").strip()
                if not name:
                    print("Application name cannot be empty. Please try again.")
                    continue
                if name in vault_data["services"]:
                    print(f"'{name}' already exists. Please choose a different name.")
                    continue
                break
        else:
            name = args.name
            if name in vault_data["services"]:
                self.print_error(f"'{name}' already exists.")
                return 1

        # Generate password
        password = generate_password(
            length=args.length,
            use_symbols=args.symbols,
            use_digits=args.digits,
            use_uppercase=args.uppercase,
        )

        # Add to vault
        vault_data["services"][name] = {"password": password}

        if self.manager.save_vault_data(vault_data, master_password):
            self.print_success(f"Password saved for '{name}'")
        else:
            self.print_error("Failed to save password.")
            return 1

        print(f"Generated password: {password}")

        # Copy to clipboard
        clipboard = ClipboardManager()
        if clipboard.copy(password):
            self.print_success("Copied to clipboard!")
        else:
            self.print_error("Failed to copy to clipboard.")

        if args.verbose:
            print(
                f"Password generated with length {args.length}, "
                f"symbols={args.symbols}, digits={args.digits}, "
                f"uppercase={args.uppercase}."
            )

        return 0
