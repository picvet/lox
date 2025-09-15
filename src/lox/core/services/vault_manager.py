"""Vault management service for handling password storage operations."""

import logging
from typing import Any, Dict, Optional

from ..exceptions import VaultError, VaultNotFoundError, VaultOperationError
from ..storage import Vault

logger = logging.getLogger(__name__)


class VaultManager:
    """Manages all interactions with the password vault."""

    def __init__(self, vault: Vault):
        """
        Initialize VaultManager with a vault instance.

        Args:
            vault: Vault instance for storage operations
        """
        self._vault = vault

    def get_vault_data(self, master_password: str) -> Dict[str, Any]:
        """
        Load and return vault data.

        Args:
            master_password: Master password for decryption

        Returns:
            Decrypted vault data

        Raises:
            VaultNotFoundError: If vault doesn't exist
            VaultOperationError: If decryption fails
        """
        if not self._vault.vault_exists():
            raise VaultNotFoundError("No vault exists. Use 'lox init' to create one.")

        try:
            return self._vault.load_vault(master_password)
        except Exception as e:
            raise VaultOperationError(f"Failed to load vault: {e}") from e

    def add_password_entry(
        self, name: str, password: str, vault_data: Dict[str, Any]
    ) -> None:
        """
        Add a new password entry to vault data.

        Args:
            name: Service name identifier
            password: Password to store
            vault_data: Vault data to modify

        Raises:
            VaultError: If service already exists
        """
        if name in vault_data.get("services", {}):
            raise VaultError(f"Service '{name}' already exists in vault.")

        vault_data.setdefault("services", {})[name] = {"password": password}

    def update_password_entry(
        self, name: str, password: str, vault_data: Dict[str, Any]
    ) -> None:
        """
        Update an existing password entry.

        Args:
            name: Service name identifier
            password: New password to store
            vault_data: Vault data to modify

        Raises:
            VaultError: If service doesn't exist
        """
        if name not in vault_data.get("services", {}):
            raise VaultError(f"Service '{name}' not found in vault.")

        vault_data["services"][name]["password"] = password

    def delete_password_entry(self, name: str, vault_data: Dict[str, Any]) -> bool:
        """
        Delete a password entry from vault data.

        Args:
            name: Service name identifier
            vault_data: Vault data to modify

        Returns:
            True if entry was deleted, False if not found
        """
        if name in vault_data.get("services", {}):
            del vault_data["services"][name]
            return True
        return False

    def save_vault_data(self, vault_data: Dict[str, Any], master_password: str) -> bool:
        """
        Save updated vault data.

        Args:
            vault_data: Vault data to save
            master_password: Master password for encryption

        Returns:
            True if save successful

        Raises:
            VaultOperationError: If encryption or save fails
        """
        try:
            return self._vault.save_vault(vault_data, master_password)
        except Exception as e:
            raise VaultOperationError(f"Failed to save vault: {e}") from e

    def vault_exists(self) -> bool:
        """Check if vault file exists."""
        return self._vault.vault_exists()

    def initialize_vault(self, master_password: str) -> bool:
        """
        Initialize a new empty vault.

        Args:
            master_password: Master password for encryption

        Returns:
            True if initialization successful
        """
        try:
            empty_vault = {"services": {}, "metadata": {"version": "1.0"}}
            return self._vault.save_vault(empty_vault, master_password)
        except Exception as e:
            raise VaultOperationError(f"Failed to initialize vault: {e}") from e

    def get_service_names(self, vault_data: Dict[str, Any]) -> list:
        """
        Get list of all service names in vault.

        Args:
            vault_data: Vault data to inspect

        Returns:
            List of service names
        """
        return list(vault_data.get("services", {}).keys())

    def get_password(
        self, service_name: str, vault_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get password for a specific service.

        Args:
            service_name: Name of the service
            vault_data: Vault data to search

        Returns:
            Password string or None if service not found
        """
        service = vault_data.get("services", {}).get(service_name)
        return service.get("password") if service else None
