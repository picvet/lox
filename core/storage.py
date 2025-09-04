import json
import os
from typing import Any, Dict

from core.crypto import decrypt_data, derive_key, encrypt_data


class VaultError(Exception):
    """Custom exception for errors related to vault operations."""

    pass


class Vault:
    def __init__(self, vault_path: str = "data/vault.enc"):
        self.vault_path = vault_path
        self.ensure_data_dir()

    def ensure_data_dir(self):
        """Ensure the data directory exists."""
        directory = os.path.dirname(self.vault_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def vault_exists(self) -> bool:
        """Check if the vault file exists."""
        return os.path.exists(self.vault_path)

    def initialize_vault(self, master_password: str) -> bool:
        """
        Initialize a new empty vault.
        Returns False if the vault already exists.
        """
        if self.vault_exists():
            print("Vault already exists. Use 'load' to open it.")
            return False

        empty_vault = {"services": {}}
        return self.save_vault(empty_vault, master_password)

    def save_vault(self, data: Dict[str, Any], master_password: str) -> bool:
        """
        Encrypt and save the vault data.
        Returns True on success, False on failure.
        """
        try:
            key, salt = derive_key(master_password)
            json_data = json.dumps(data)
            encrypted_data = encrypt_data(json_data, key)

            with open(self.vault_path, "wb") as f:
                f.write(len(salt).to_bytes(4, "big"))
                f.write(salt)
                f.write(encrypted_data)

            return True
        except (IOError, OSError) as e:
            print(f"File system error saving vault: {e}")
            return False
        except Exception as e:
            print(f"Error saving vault: {e}")
            return False

    def load_vault(self, master_password: str) -> Dict[str, Any]:
        """
        Load and decrypt the vault data.

        Raises:
            FileNotFoundError: If the vault file doesn't exist.
            VaultError: If decryption fails (e.g., wrong password or corrupt data).
        """
        if not self.vault_exists():
            raise FileNotFoundError(
                "Vault file not found at '"
                f"{self.vault_path}'. Please initialize first."
            )

        try:
            with open(self.vault_path, "rb") as f:
                salt_length = int.from_bytes(f.read(4), "big")
                salt = f.read(salt_length)
                encrypted_data = f.read()

            key, _ = derive_key(master_password, salt=salt)

            decrypted_json = decrypt_data(encrypted_data, key)

            return json.loads(decrypted_json)

        except (ValueError, KeyError, TypeError) as e:
            raise VaultError(
                "Failed to decrypt vault. The master password may be incorrect or the file is corrupted."
            ) from e

        except Exception as e:
            raise VaultError(
                f"An unexpected error occurred while loading the vault: {e}"
            ) from e
