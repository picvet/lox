"""Secure credential management with cross-platform support."""

import getpass
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

import keyring

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    KEYRING = "keyring"
    ENV_FILE = "env_file"


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
        ]

    def store_credentials(
        self,
        role_arn: str,
        region: str,
    ) -> bool:
        """
        Store credentials using the most secure available backend.
        """
        credential_data = {
            "role_arn": role_arn,
            "region": region,
            "storage_backend": None,
        }

        # Try storage backends in order of preference
        for backend in self._backend_preference:
            try:
                storage_method = self._get_storage_method(backend)
                if storage_method(credential_data):
                    credential_data["storage_backend"] = backend.value
                    storage_method(credential_data)

                    self._used_backend = backend
                    logger.info("Credentials stored using %s backend", backend.value)
                    return True
            except Exception as e:
                logger.warning("Storage with %s failed: %s", backend.value, e)
                continue

        raise CredentialStorageError("All credential storage methods failed")

    def get_credentials(self) -> Tuple[
        Optional[str],
        Optional[str],
    ]:
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

        return None

    def _get_storage_method(self, backend: StorageBackend):
        """Get the storage method for a given backend."""
        methods = {
            StorageBackend.KEYRING: self._store_with_keyring,
            StorageBackend.ENV_FILE: self._store_with_env_file,
        }
        return methods[backend]

    def _get_from_backend(self, backend: StorageBackend) -> Optional[Tuple[str, str]]:
        """Retrieve credentials from a specific backend."""
        methods = {
            StorageBackend.KEYRING: self._get_from_keyring,
            StorageBackend.ENV_FILE: self._get_from_env_file,
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

    def _get_from_keyring(self) -> Optional[Tuple[str, str]]:
        """Retrieve credentials from keyring."""
        try:
            user = getpass.getuser()
            creds_json = keyring.get_password(
                f"{self.service_name}-credentials",
                user,
            )

            if creds_json:
                creds_data = json.loads(creds_json)

                if isinstance(creds_data, dict):
                    role_arn = creds_data.get("role_arn")
                    region = creds_data.get("region")

                    if role_arn:
                        backend_str = creds_data.get("storage_backend")
                        if backend_str:
                            try:
                                self._used_backend = StorageBackend(backend_str)
                            except ValueError:
                                pass

                        return role_arn, region
                else:
                    logger.warning("Found old credential format in keyring")
                    return None

        except (
            keyring.errors.KeyringError,
            json.JSONDecodeError,
            AttributeError,
        ) as e:
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

    def _get_from_env_file(self) -> Optional[Tuple[str, str]]:
        """Retrieve credentials from environment file."""
        try:
            env_file = (
                Path.home() / ".config" / self.service_name.lower() / "credentials.json"
            )
            if env_file.exists():
                creds_data = json.loads(env_file.read_text())

                if isinstance(creds_data, dict):
                    role_arn = creds_data.get("role_arn")
                    region = creds_data.get("region")

                    if role_arn:
                        backend_str = creds_data.get("storage_backend")
                        if backend_str:
                            try:
                                self._used_backend = StorageBackend(backend_str)
                            except ValueError:
                                pass

                        return role_arn, region

        except (IOError, json.JSONDecodeError, AttributeError) as e:
            logger.debug("Env file retrieval failed: %s", e)

        return None

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

            self._used_backend = None
        return success

    def get_storage_backend(self) -> Optional[str]:
        """Get the currently used storage backend."""
        return self._used_backend.value if self._used_backend else None
