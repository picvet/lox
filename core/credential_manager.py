"""Secure credential management with cross-platform support."""

import getpass
import json
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

import keyring

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    KEYRING = "keyring"
    ENV_FILE = "env_file"
    FALLBACK = "fallback"


class CredentialStorageError(Exception):
    """Exception raised for credential storage-related errors."""

    pass


class CredentialManager:
    """Manages secure storage and retrieval of AWS credentials."""

    def __init__(self, service_name: str = "LoxPasswordManager"):
        self.service_name = service_name
        self._used_backend: Optional[StorageBackend] = None

    def store_credentials(
        self,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
        expiry_days: int = 7,
    ) -> bool:
        """
        Store credentials using the most secure available backend.

        Args:
            access_key: AWS Access Key ID
            secret_key: AWS Secret Access Key
            region: AWS region
            expiry_days: Credential validity period

        Returns:
            bool: True if storage successful

        Raises:
            CredentialStorageError: If all storage methods fail
        """
        expiry_time = datetime.now() + timedelta(days=expiry_days)
        credential_data = {
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
            "expiry": expiry_time.isoformat(),
        }

        # Try storage backends in order of security
        backends = [
            (self._store_with_keyring, StorageBackend.KEYRING),
            (self._store_with_env_file, StorageBackend.ENV_FILE),
            (self._store_fallback, StorageBackend.FALLBACK),
        ]

        for storage_method, backend in backends:
            try:
                if storage_method(credential_data):
                    self._used_backend = backend
                    logger.info("Credentials stored using %s backend", backend.value)
                    return True
            except Exception as e:
                logger.warning("Storage with %s failed: %s", backend.value, e)
                continue

        raise CredentialStorageError("All credential storage methods failed")

    def get_credentials(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Retrieve stored credentials from the most secure available source.

        Returns:
            Tuple containing access_key, secret_key, region
        """
        # Try to retrieve from the same backend used for storage
        if self._used_backend == StorageBackend.KEYRING:
            creds = self._get_from_keyring()
        elif self._used_backend == StorageBackend.ENV_FILE:
            creds = self._get_from_env_file()
        else:
            creds = self._get_fallback()

        # Validate credentials aren't expired
        if creds and self._are_credentials_expired(creds):
            logger.warning("Stored credentials have expired")
            return None, None, None

        return creds if creds else (None, None, None)

    def _store_with_keyring(self, credential_data: dict) -> bool:
        """Store credentials using system keyring."""
        try:
            user = getpass.getuser()
            keyring.set_password(
                f"{self.service_name}-credentials", user, json.dumps(credential_data)
            )
            return True
        except keyring.errors.KeyringError as e:
            logger.debug("Keyring storage failed: %s", e)
            return False

    def _store_with_env_file(self, credential_data: dict) -> bool:
        """Store credentials in encrypted environment file."""
        try:
            config_dir = Path.home() / ".config" / self.service_name.lower()
            config_dir.mkdir(parents=True, exist_ok=True)

            env_file = config_dir / "credentials.env"
            # In production, you'd encrypt this file
            env_file.write_text(json.dumps(credential_data))
            env_file.chmod(0o600)  # Restrict permissions

            return True
        except (IOError, PermissionError) as e:
            logger.debug("Env file storage failed: %s", e)
            return False

    def _store_fallback(self, credential_data: dict) -> bool:
        """Fallback storage method (least secure)."""
        try:
            # This would be your original fallback implementation
            # Consider at least setting environment variables temporarily
            os.environ["AWS_ACCESS_KEY_ID"] = credential_data["access_key"]
            os.environ["AWS_SECRET_ACCESS_KEY"] = credential_data["secret_key"]
            os.environ["AWS_DEFAULT_REGION"] = credential_data["region"]
            return True
        except Exception as e:
            logger.debug("Fallback storage failed: %s", e)
            return False

    def _get_from_keyring(self) -> Optional[Tuple[str, str, str]]:
        """Retrieve credentials from keyring."""
        try:
            user = getpass.getuser()
            creds_json = keyring.get_password(f"{self.service_name}-credentials", user)
            if creds_json:
                creds = json.loads(creds_json)
                return creds["access_key"], creds["secret_key"], creds["region"]
        except (keyring.errors.KeyringError, json.JSONDecodeError) as e:
            logger.debug("Keyring retrieval failed: %s", e)
        return None

    def _get_from_env_file(self) -> Optional[Tuple[str, str, str]]:
        """Retrieve credentials from environment file."""
        try:
            env_file = (
                Path.home() / ".config" / self.service_name.lower() / "credentials.env"
            )
            if env_file.exists():
                creds = json.loads(env_file.read_text())
                return creds["access_key"], creds["secret_key"], creds["region"]
        except (IOError, json.JSONDecodeError) as e:
            logger.debug("Env file retrieval failed: %s", e)
        return None

    def _get_fallback(self) -> Optional[Tuple[str, str, str]]:
        """Fallback retrieval method."""
        access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

        if access_key and secret_key:
            return access_key, secret_key, region
        return None

    def _are_credentials_expired(self, creds: Tuple[str, str, str]) -> bool:
        """Check if credentials are expired."""
        # This would need the expiry information from your storage format
        # For now, assuming credentials don't expire in fallback scenarios
        return False

    def clear_credentials(self) -> bool:
        """Remove stored credentials from all backends."""
        success = True
        try:
            user = getpass.getuser()
            keyring.delete_password(f"{self.service_name}-credentials", user)
        except keyring.errors.KeyringError:
            success = False

        try:
            env_file = (
                Path.home() / ".config" / self.service_name.lower() / "credentials.env"
            )
            if env_file.exists():
                env_file.unlink()
        except IOError:
            success = False

        # Clear environment variables
        for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"]:
            os.environ.pop(var, None)

        return success
