import getpass
import sys

from core.clipboard import copy_to_clipboard
from core.password_gen import generate_password
from core.storage import Vault


class VaultManager:
    """Manages all interactions with the password vault file."""

    def __init__(self, vault):
        self._vault = vault

    def get_vault_data(self, master_password):
        """Loads and returns vault data, or raises an error on failure."""
        if not self._vault.vault_exists():
            raise FileNotFoundError("No vault exists. Use 'lox init' to create one.")

        try:
            return self._vault.load_vault(master_password)
        except Exception as e:
            raise ValueError(f"Failed to load vault: {e}.")

    def add_password_entry(self, name, password, vault_data):
        """Adds a new password to the vault data."""
        if name in vault_data["services"]:
            raise ValueError(f"'{name}' already exists.")

        vault_data["services"][name] = {"password": password}

    def save_vault_data(self, vault_data, master_password):
        """Saves the updated vault data."""
        return self._vault.save_vault(vault_data, master_password)


def handle_add_command(args):
    """Handles the 'add' command to add a password to the vault."""
    try:
        vault = Vault()
        manager = VaultManager(vault)

        master_password = getpass.getpass("Enter master password: ")

        vault_data = manager.get_vault_data(master_password)

        # This part of the logic remains in the handler
        while True:
            name = input("Enter name of application: ").strip()
            if not name:
                print("Application name cannot be empty. Please try again.")
                continue

            try:
                manager.add_password_entry(
                    name, "dummy", vault_data
                )  # Check if name exists
                vault_data["services"].pop(name)  # Remove dummy entry
                break
            except ValueError as e:
                print(e)
                continue

        # Generate the new password
        password = generate_password(
            length=args.length,
            use_symbol=args.symbols,
            use_digits=args.digits,
            use_uppercase=args.uppercase,
        )

        # Add the real entry and save
        manager.add_password_entry(name, password, vault_data)

        if manager.save_vault_data(vault_data, master_password):
            print(f"✓ Password saved for '{name}'")
            print(f"Generated password: {password}")
            if copy_to_clipboard(password):
                print("✓ Copied to clipboard!")
            else:
                print("✗ Failed to copy to clipboard.")
        else:
            print("✗ Failed to save password.")

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
