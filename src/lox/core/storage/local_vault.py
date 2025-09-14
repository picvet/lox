"""Local encrypted vault file storage implementation."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..cryptography import decrypt_data, derive_key, encrypt_data
from ..exceptions import VaultNotFoundError, VaultOperationError

logger = logging.getLogger(__name__)


class Vault:
    """Manages local encrypted vault file storage."""

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize vault with optional custom path.

        Args:
            vault_path: Custom path to vault file. Defaults to "~/.config/loxpasswordmanager/vault.enc"
        """
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = (
                Path.home() / ".config" / "loxpasswordmanager" / "vault.enc"
            )

        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)

    def vault_exists(self) -> bool:
        """Check if vault file exists."""
        return self.vault_path.exists()

    def initialize_vault(self, master_password: str) -> bool:
        """
        Initialize a new empty vault.

        Args:
            master_password: Master password for encryption

        Returns:
            True if successful, False if vault already exists

        Raises:
            VaultOperationError: If initialization fails
        """
        if self.vault_exists():
            logger.warning("Vault already exists at %s", self.vault_path)
            return False

        try:
            empty_vault = {"services": {}, "metadata": {"version": "1.0"}}
            return self.save_vault(empty_vault, master_password)
        except Exception as e:
            raise VaultOperationError(f"Failed to initialize vault: {e}") from e

    def save_vault(self, data: Dict[str, Any], master_password: str) -> bool:
        """
        Encrypt and save the vault data.

        Args:
            data: Vault data to save
            master_password: Master password for encryption

        Returns:
            True if save successful

        Raises:
            VaultOperationError: If encryption or save fails
        """
        try:
            key, salt = derive_key(master_password)
            json_data = json.dumps(data, indent=2)
            encrypted_data = encrypt_data(json_data, key)

            with open(self.vault_path, "wb") as f:
                f.write(len(salt).to_bytes(4, "big"))
                f.write(salt)
                f.write(encrypted_data)

            logger.info("Vault saved successfully to %s", self.vault_path)
            return True

        except (IOError, OSError) as e:
            error_msg = f"File system error saving vault: {e}"
            logger.error(error_msg)
            raise VaultOperationError(error_msg) from e
        except Exception as e:
            error_msg = f"Error saving vault: {e}"
            logger.error(error_msg)
            raise VaultOperationError(error_msg) from e

    def load_vault(self, master_password: str) -> Dict[str, Any]:
        """
        Load and decrypt the vault data.

        Args:
            master_password: Master password for decryption

        Returns:
            Decrypted vault data

        Raises:
            VaultNotFoundError: If vault file doesn't exist
            VaultOperationError: If decryption fails
        """
        if not self.vault_exists():
            raise VaultNotFoundError(
                f"Vault file not found at '{
                    self.vault_path}'. Please initialize first."
            )

        try:
            with open(self.vault_path, "rb") as f:
                salt_length = int.from_bytes(f.read(4), "big")
                salt = f.read(salt_length)
                encrypted_data = f.read()

            key, _ = derive_key(master_password, salt=salt)
            decrypted_json = decrypt_data(encrypted_data, key)

            vault_data = json.loads(decrypted_json)

            logger.info("Vault loaded successfully from %s", self.vault_path)
            return vault_data

        except (ValueError, KeyError, TypeError) as e:
            error_msg = (
                "Failed to decrypt vault. The master password may be incorrect "
                "or the file is corrupted."
            )
            logger.error(error_msg)
            raise VaultOperationError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error while loading vault: {e}"
            logger.error(error_msg)
            raise VaultOperationError(error_msg) from e

    def get_encrypted_vault(self) -> bytes:
        """
        Read the raw, encrypted vault data from the file.

        Returns:
            Encrypted vault data as bytes

        Raises:
            VaultNotFoundError: If vault file doesn't exist
            VaultOperationError: If reading fails
        """
        if not self.vault_exists():
            raise VaultNotFoundError(
                f"Vault file not found at '{
                    self.vault_path}'. Please initialize first."
            )

        try:
            with open(self.vault_path, "rb") as f:
                encrypted_data = f.read()

            logger.debug("Read encrypted vault data from %s", self.vault_path)
            return encrypted_data

        except IOError as e:
            error_msg = f"Error reading encrypted vault file: {e}"
            logger.error(error_msg)
            raise VaultOperationError(error_msg) from e

    def sync_replace_local_file_content(self, cloud_bytes_content: bytes) -> bool:
        """
        Replace local vault file content with cloud version.

        Args:
            cloud_bytes_content: Encrypted vault data from cloud

        Returns:
            True if replacement successful

        Raises:
            VaultOperationError: If writing fails
        """
        try:
            self._ensure_data_dir()

            with open(self.vault_path, "wb") as f:
                f.write(cloud_bytes_content)

            logger.info("Local vault synchronized with cloud version")
            return True

        except IOError as e:
            error_msg = f"Error writing to vault file: {e}"
            logger.error(error_msg)
            raise VaultOperationError(error_msg) from e

    def delete_vault(self) -> bool:
        """
        Delete the vault file.

        Returns:
            True if deletion successful, False if file didn't exist
        """
        try:
            if self.vault_exists():
                self.vault_path.unlink()
                logger.info("Vault deleted: %s", self.vault_path)
                return True
            return False
        except OSError as e:
            logger.error("Error deleting vault: %s", e)
            return False

    def get_vault_size(self) -> Optional[int]:
        """
        Get the size of the vault file in bytes.

        Returns:
            File size in bytes or None if file doesn't exist
        """
        if self.vault_exists():
            return self.vault_path.stat().st_size
        return None

    def get_vault_info(self) -> Dict[str, Any]:
        """
        Get information about the vault file.

        Returns:
            Dictionary with vault information
        """
        info = {
            "path": str(self.vault_path),
            "exists": self.vault_exists(),
            "size_bytes": self.get_vault_size(),
        }

        if self.vault_exists():
            info["modified"] = self.vault_path.stat().st_mtime

        return info
