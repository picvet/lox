import getpass
import os
import sys

from core.clipboard import copy_to_clipboard
from core.core import VaultManager
from core.password_gen import generate_password
from core.storage import Vault


def handle_add_command(args):
    """Handle add command - add a password to the vault."""
    try:
        # Create instances of the core classes
        vault = Vault()
        manager = VaultManager(vault)

        # Get the master password from the user
        master_password = getpass.getpass("Enter master password: ")

        # Load the vault data using the manager
        try:
            vault_data = manager.get_vault_data(master_password)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}.")
            return

        # Get the application name from the user with validation
        if not args.name:
            while True:
                name = input("Enter name of application: ").strip()
                if not name:
                    print("Application name cannot be empty. Please try again.")
                    continue

                # Check if the name already exists in the vault
                if name in vault_data["services"]:
                    print(f"'{name}' already exists. Please choose a different name.")
                    continue

                break
        else:
            name = args.name
            if name in vault_data["services"]:
                print(f"Error: '{name}' already exists.")
                return

        # Generate the new password
        password = generate_password(
            length=args.length,
            use_symbols=args.symbols,
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
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


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


def handle_get_command(args):
    try:
        vault = Vault()
        manager = VaultManager(vault)

        master_password = getpass.getpass("Enter master password: ")

        try:
            vault_data = manager.get_vault_data(master_password)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            return

        name = args.name

        if name not in vault_data["services"]:
            print(f"Error: '{name}' not found in the vault.")
            return

        password = vault_data["services"][name]["password"]
        print(f"Password for '{name}': {password}")

        if copy_to_clipboard(password):
            print("✓ Copied to clipboard!")
        else:
            print("✗ Failed to copy to clipboard.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def handle_delete_command(args):
    try:
        vault = Vault()
        manager = VaultManager(vault)

        master_password = getpass.getpass("Enter master password: ")

        try:
            vault_data = manager.get_vault_data(master_password)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            return

        name = args.name

        if name not in vault_data["services"]:
            print(f"Error: '{name}' not found in the vault.")
            return

        confirmation = input(f"Are you sure you want to delete {name} ? (y/n): ")

        if confirmation.lower() not in ["y", "yes"]:
            print("Delete cancelled.")
            return

        del vault_data["services"][name]

        if manager.save_vault_data(vault_data, master_password):
            print(f"✓ Password for '{name}' deleted.")
        else:
            print(f"✗ Failed to delete password for '{name}'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def handle_list_command():
    try:
        vault = Vault()
        manager = VaultManager(vault)

        master_password = getpass.getpass("Enter master password: ")

        try:
            vault_data = manager.get_vault_data(master_password)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            return

        services = vault_data.get("services", {})
        if not services:
            print("No services stored in the vault.")
            return

        print("Stored services:")
        for name in services.keys():
            print(f"- {name}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def handle_push_command():
    try:
        from core.resources.aws.aws_dynamo_service import DynamoDBService

        DynamoDBService().put_item(common_name="PERCY_PASS")
    except Exception as e:
        print(f"Error pushing to sync: {e}")


def handle_pull_command():
    from core.resources.aws.aws_dynamo_service import DynamoDBService

    print(DynamoDBService().get_last_item_query())
