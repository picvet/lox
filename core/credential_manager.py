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
        self._backend_preference = [
            StorageBackend.KEYRING,
            StorageBackend.ENV_FILE,
            StorageBackend.FALLBACK,
        ]

    def store_credentials(
        self,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
        expiry_days: int = 7,
    ) -> bool:
        """
        Store credentials using the most secure available backend.
        """
        expiry_time = datetime.now() + timedelta(days=expiry_days)
        credential_data = {
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
            "expiry": expiry_time.isoformat(),
            "storage_backend": None,  # Will be set by successful storage
        }

        # Try storage backends in order of preference
        for backend in self._backend_preference:
            try:
                storage_method = self._get_storage_method(backend)
                if storage_method(credential_data):
                    # Update credential data with backend info
                    credential_data["storage_backend"] = backend.value
                    # Re-store with backend info
                    storage_method(credential_data)

                    self._used_backend = backend
                    logger.info("Credentials stored using %s backend", backend.value)
                    return True
            except Exception as e:
                logger.warning("Storage with %s failed: %s", backend.value, e)
                continue

        raise CredentialStorageError("All credential storage methods failed")

    def get_credentials(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Retrieve stored credentials by trying all backends in order.
        """
        # First, try to get from the last used backend (if known)
        if self._used_backend:
            creds = self._get_from_backend(self._used_backend)
            if creds and not self._are_credentials_expired(creds):
                return creds

        # If no stored backend or retrieval failed, try all backends in order
        for backend in self._backend_preference:
            try:
                creds = self._get_from_backend(backend)
                if creds:
                    # Check if credentials include backend info
                    if isinstance(creds, tuple) and len(creds) == 3:
                        # Regular tuple format, check expiry
                        if not self._are_credentials_expired(creds):
                            self._used_backend = backend
                            return creds
                    else:
                        # Shouldn't happen, but handle gracefully
                        logger.warning(
                            "Unexpected credential format from %s", backend.value
                        )
            except Exception as e:
                logger.debug("Retrieval from %s failed: %s", backend.value, e)
                continue

        # Final fallback to environment variables
        return self._get_fallback()

    def _get_storage_method(self, backend: StorageBackend):
        """Get the storage method for a given backend."""
        methods = {
            StorageBackend.KEYRING: self._store_with_keyring,
            StorageBackend.ENV_FILE: self._store_with_env_file,
            StorageBackend.FALLBACK: self._store_fallback,
        }
        return methods[backend]

    def _get_from_backend(
        self, backend: StorageBackend
    ) -> Optional[Tuple[str, str, str]]:
        """Retrieve credentials from a specific backend."""
        methods = {
            StorageBackend.KEYRING: self._get_from_keyring,
            StorageBackend.ENV_FILE: self._get_from_env_file,
            StorageBackend.FALLBACK: self._get_fallback,
        }
        return methods[backend]()

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

    def _get_from_keyring(self) -> Optional[Tuple[str, str, str]]:
        """Retrieve credentials from keyring."""
        try:
            user = getpass.getuser()
            creds_json = keyring.get_password(f"{self.service_name}-credentials", user)

            if creds_json:
                creds_data = json.loads(creds_json)

                # Handle both old format (tuple) and new format (dict with backend info)
                if isinstance(creds_data, dict):
                    # New format with metadata
                    access_key = creds_data.get("access_key")
                    secret_key = creds_data.get("secret_key")
                    region = creds_data.get("region", "us-east-1")

                    if access_key and secret_key:
                        # Update the used backend if stored in metadata
                        backend_str = creds_data.get("storage_backend")
                        if backend_str:
                            try:
                                self._used_backend = StorageBackend(backend_str)
                            except ValueError:
                                pass

                        return access_key, secret_key, region
                else:
                    # Old format - try to parse as tuple (backward compatibility)
                    logger.warning("Found old credential format in keyring")
                    return None

        except (keyring.errors.KeyringError, json.JSONDecodeError, AttributeError) as e:
            logger.debug("Keyring retrieval failed: %s", e)

        return None

    def _store_with_env_file(self, credential_data: dict) -> bool:
        """Store credentials in environment file."""
        try:
            config_dir = Path.home() / ".config" / self.service_name.lower()
            config_dir.mkdir(parents=True, exist_ok=True)

            env_file = config_dir / "credentials.json"
            env_file.write_text(json.dumps(credential_data, indent=2))
            env_file.chmod(0o600)

            return True
        except (IOError, PermissionError) as e:
            logger.debug("Env file storage failed: %s", e)
            return False

    def _get_from_env_file(self) -> Optional[Tuple[str, str, str]]:
        """Retrieve credentials from environment file."""
        try:
            env_file = (
                Path.home() / ".config" / self.service_name.lower() / "credentials.json"
            )
            if env_file.exists():
                creds_data = json.loads(env_file.read_text())

                if isinstance(creds_data, dict):
                    access_key = creds_data.get("access_key")
                    secret_key = creds_data.get("secret_key")
                    region = creds_data.get("region", "us-east-1")

                    if access_key and secret_key:
                        # Update the used backend if stored in metadata
                        backend_str = creds_data.get("storage_backend")
                        if backend_str:
                            try:
                                self._used_backend = StorageBackend(backend_str)
                            except ValueError:
                                pass

                        return access_key, secret_key, region

        except (IOError, json.JSONDecodeError, AttributeError) as e:
            logger.debug("Env file retrieval failed: %s", e)

        return None

    def _store_fallback(self, credential_data: dict) -> bool:
        """Fallback storage method."""
        try:
            # Store in environment variables (temporary)
            os.environ["AWS_ACCESS_KEY_ID"] = credential_data["access_key"]
            os.environ["AWS_SECRET_ACCESS_KEY"] = credential_data["secret_key"]
            os.environ["AWS_DEFAULT_REGION"] = credential_data["region"]
            return True
        except Exception as e:
            logger.debug("Fallback storage failed: %s", e)
            return False

    def _get_fallback(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Fallback retrieval method."""
        access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

        return access_key, secret_key, region

    def _are_credentials_expired(self, creds: Tuple[str, str, str]) -> bool:
        """Check if credentials are expired."""
        # For now, assume credentials don't expire in basic storage
        # In a real implementation, you'd check the expiry timestamp
        return False

    def clear_credentials(self) -> bool:
        """Remove stored credentials from all backends."""
        success = True

        # Clear keyring
        try:
            user = getpass.getuser()
            keyring.delete_password(f"{self.service_name}-credentials", user)
        except keyring.errors.KeyringError:
            success = False

        # Clear env file
        try:
            env_file = (
                Path.home() / ".config" / self.service_name.lower() / "credentials.json"
            )
            if env_file.exists():
                env_file.unlink()
        except IOError:
            success = False

        # Clear environment variables
        for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"]:
            os.environ.pop(var, None)

        self._used_backend = None
        return success

    def get_storage_backend(self) -> Optional[str]:
        """Get the currently used storage backend."""
        return self._used_backend.value if self._used_backend else None
