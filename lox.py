import argparse
import getpass
import os

from core.clipboard import copy_to_clipboard
from core.password_gen import generate_password
from core.storage import Vault


def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="Lox - A simple CLI password manager", prog="lox"
    )

    # Global arguments that must come BEFORE the subcommand
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Init command - Create a new vault
    subparsers.add_parser(
        "init",
        help="Initialize a new password vault",
    )

    # Reset command - Rest the vault
    subparsers.add_parser(
        "reset",
        help="Reset the vault (deletes all data)",
    )

    # Generate command parser
    parser_generate = subparsers.add_parser(
        "generate",
        help="Generate a new random password",
    )
    parser_generate.add_argument(
        "--name",
        "-n",
        help="Name to associate with this password (for saving later)",
    )
    parser_generate.add_argument(
        "--length",
        "-l",
        type=int,
        default=16,
        help="Length of the password (default: 16)",
    )
    parser_generate.add_argument(
        "--no-symbols",
        action="store_false",
        dest="symbols",
        help="Exclude symbols from the password",
    )
    parser_generate.add_argument(
        "--no-digits",
        action="store_false",
        dest="digits",
        help="Exclude digits from the password",
    )
    parser_generate.add_argument(
        "--no-uppercase",
        action="store_false",
        dest="uppercase",
        help="Exclude uppercase letters from the password",
    )
    parser_generate.add_argument(
        "--copy",
        "-c",
        action="store_true",
        help="Copy the generated password to clipboard",
    )

    # Add command - Add a password to the vault
    parser_add = subparsers.add_parser(
        "add",
        help="Add a password to the vault",
    )
    parser_add.add_argument(
        "service",
        help="Name of the service (e.g. github, email)",
    )
    parser_add.add_argument(
        "--username",
        "-u",
        required=True,
        help="Username for the service",
    )
    parser_add.add_argument(
        "--password",
        "-p",
        help="Password to store {prompt if not provided}",
    )
    parser_add.add_argument(
        "--vault-path",
        default="data/vault.enc",
        help="Path to the vault file",
    )

    # List command - Show all services in vault
    parser_list = subparsers.add_parser("list", help="List all services in the vault")
    parser_list.add_argument(
        "--vault-path",
        default="data/vault.enc",
        help="Path to the vault file",
    )

    args = parser.parse_args()

    if args.command == "init":
        handle_init_command()
    elif args.command == "generate":
        handle_generate_command(args)
    elif args.command == "reset":
        handle_reset_command()
    elif args.command == "add":
        handle_add_command(args)
    elif args.command == "list":
        handle_list_command(args)


def handle_init_command():
    """Handle the init command - create a new vault"""
    vault = Vault()

    if vault.vault_exists():
        print("Vault already exists. Use 'lox reset' to create a new vault.")
        return

    print("Initializing new Lox password vault...")
    print(
        "⚠️  Warning: If you forget this password, you'll lose access to your stored credentials."
    )
    print()

    # Get master password with confirmation
    while True:
        master_password = getpass.getpass("Enter master password: ")
        if not master_password.strip():
            # FIXED: mepty -> empty
            print("Password cannot be empty. Please try again.")
            continue

        confirm_password = getpass.getpass("Confirm master password: ")

        if master_password == confirm_password:
            break
        else:
            print("Passwords do not match. Please try again.")
            print()

    # Initialize the vault
    if vault.initialize_vault(master_password):
        print("✓ Vault created successfully!")
        print("You can now add credentials using 'lox add' command.")
    else:
        print("✗ Failed to create vault. Please try again.")


def handle_generate_command(args):
    """Handle generate command - create and save passwords."""
    try:
        password = generate_password(
            length=args.length,
            use_symbols=args.symbols,  # FIXED: use_symbol -> use_symbols
            use_digits=args.digits,
            use_uppercase=args.uppercase,
        )

        print(f"Generated password: {password}")

        # Only copy if --copy flag is provided
        if args.copy:
            if copy_to_clipboard(password):
                print("✓ Copied to clipboard!")
            else:
                print("✗ Failed to copy to clipboard")

        if args.name and args.verbose:
            print(f"Password generated for: {args.name}")

    except ValueError as e:
        print(f"Error: {e}")


def handle_reset_command():
    """Handle reset command - delete and recreate vault."""
    vault = Vault()

    if not vault.vault_exists():
        # FIXED: value -> vault
        print("No vault exists. Use 'lox init' to create one.")
        return

    print("⚠️  WARNING: This will delete ALL stored credentials!")
    print("You will lose access to all passwords permanently.")
    print()

    confirmation = input("Are you sure you want to reset the vault? (y/n): ")

    if confirmation.lower() not in ["y", "yes"]:
        print("Reset cancelled.")
        return

    # Delete the vault file
    try:
        os.remove(vault.vault_path)
        print("✓ Vault deleted.")
        print()

        # Now initialize a new vault
        handle_init_command()

    except Exception as e:
        print(f"✗ Error resetting vault: {e}")


# Placeholder functions for add and list commands
def handle_add_command(args):
    """Handle add command - add a password to the vault."""
    print("Add command not yet implemented.")
    print(f"Would add service: {args.service}")
    print(f"Username: {args.username}")
    if args.password:
        print(f"Password: {args.password}")
    else:
        print("Password would be prompted")


def handle_list_command(args):
    """Handle list command - show all services in vault."""
    print("List command not yet implemented.")
    print(f"Would list services from: {args.vault_path}")


if __name__ == "__main__":
    main()
