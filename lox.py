import argparse
import getpass
import os
import sys

from core.core import VaultManager, copy_to_clipboard, generate_password
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

    # Add command parser
    parser_add = subparsers.add_parser(
        "add",
        help="Add a new credential entry",
    )
    parser_add.add_argument(
        "--length",
        "-l",
        type=int,
        default=16,
        help="Length of the password (default: 16)",
    )
    parser_add.add_argument(
        "--no-symbols",
        action="store_false",
        dest="symbols",
        help="Exclude symbols from the password",
    )
    parser_add.add_argument(
        "--no-digits",
        action="store_false",
        dest="digits",
        help="Exclude digits from the password",
    )
    parser_add.add_argument(
        "--no-uppercase",
        action="store_false",
        dest="uppercase",
        help="Exclude uppercase letters from the password",
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


def handle_reset_command():
    """Handle reset command - delete and recreate vault."""
    vault = Vault()

    if not vault.vault_exists():
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


def _get_application_name(vault: Vault, master_password: str) -> str:
    """
    Prompts the user for a new application name and validates the input.
    Checks if the name already exists in the vault.
    """


# Placeholder functions for add and list commands


def handle_add_command(args):
    """Handle add command - add a password to the vault."""
    try:
        # Create instances of the core classes
        vault = Vault()
        manager = VaultManager(vault)

        # Get the master password from the user
        master_password = getpass.getpass("Enter master password: ")

        # Load the vault data using the manager
        # The manger handles all th eerror checking (vault exists, master
        # password is incorrect)
        try:
            vault_data = manager.get_vault_data(master_password)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}.")
            return

        # Get the application name from the user with vaulidation
        while True:
            name = input("Enter name of application: ").strip()
            if not name:
                print("Application name cannot be empty. Please try again.")
                continue

            # check if the name already exists in the vault
            if name in vault_data["services"]:
                print(f"'{name}' already exists. Please choose a different name.")
                continue

            break

        # Generate the new password
        password = generate_password(
            length=args.length,
            use_symbol=args.symbols,
            use_digits=args.digits,
            use_uppercase=args.uppercase,
        )

        # Add new password entry
        vault_data["services"][name] = {"password": password}

        # Save the updated vault
        if manager.save_vault_data(vault_data, master_password):
            print(f"✓ Password saved for '{name}'")
        else:
            print("✗ Failed to save password.")
            return

        # Handle clipboard and verbose output
        print(f"Generated password: {password}")
        if copy_to_clipboard(password):
            print("✓ Copied to clipboard!")
        else:
            print("✗ Failed to copy to clipboard.")

        if args.verbose:
            print(
                f"Password generated with length {args.length}, symbols={
                    args.symbols}, digits={args.digits}, uppercase={args.uppercase}."
            )
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        sys.exit(1)


def handle_list_command(args):
    """Handle list command - show all services in vault."""
    print("List command not yet implemented.")
    print(f"Would list services from: {args.vault_path}")


if __name__ == "__main__":
    main()
