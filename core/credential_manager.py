"""Secure credential management with cross-platform support."""

import getpass
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple

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
        access_key: str,
        secret_key: str,
    ) -> bool:
        """
        Store credentials using the most secure available backend.
        """
        credential_data = {
            "role_arn": role_arn,
            "access_key": access_key,
            "secret_key": secret_key,
        }

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

    def get_credentials(self) -> Optional[Dict[str, str]]:
        """
        Retrieve stored credentials by trying all backends in order.
        """
        if self._used_backend:
            creds = self._get_from_backend(self._used_backend)
            if creds:
                return creds

        for backend in self._backend_preference:
            try:
                creds = self._get_from_backend(backend)
                if creds:
                    return self.normalize_credentials(creds)
            except Exception as e:
                logger.debug("Retrieval from %s failed: %s", backend.value, e)
                continue

        return None

    def normalize_credentials(self, creds) -> Dict[str, str]:
        if isinstance(creds, tuple):
            role_arn, access_key, secret_key = creds
            return {
                "role_arn": role_arn,
                "access_key": access_key,
                "secret_key": secret_key,
            }
        elif isinstance(creds, dict):
            return creds
        else:
            logger.warning(f"Unexpected credential format: {creds}")

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

    def _get_from_keyring(self) -> Optional[Tuple[str, str, str, str]]:
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
                    access_key = creds_data.get("access_key")
                    secret_key = creds_data.get("secret_key")

                    if role_arn:
                        backend_str = creds_data.get("storage_backend")
                        if backend_str:
                            try:
                                self._used_backend = StorageBackend(backend_str)
                            except ValueError:
                                pass

                        return role_arn, access_key, secret_key
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

    def _get_from_env_file(self) -> Optional[Tuple[str, str, str, str]]:
        """Retrieve credentials from environment file."""
        try:
            env_file = (
                Path.home() / ".config" / self.service_name.lower() / "credentials.json"
            )
            if env_file.exists():
                creds_data = json.loads(env_file.read_text())

                if isinstance(creds_data, dict):
                    role_arn = creds_data.get("role_arn")
                    access_key = creds_data.get("access_key")
                    secret_key = creds_data.get("secret_key")

                    if role_arn:
                        backend_str = creds_data.get("storage_backend")
                        if backend_str:
                            try:
                                self._used_backend = StorageBackend(backend_str)
                            except ValueError:
                                pass

                        return role_arn, access_key, secret_key

        except (IOError, json.JSONDecodeError, AttributeError) as e:
            logger.debug("Env file retrieval failed: %s", e)

        return None

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
                Path.home() / ".config" / self.service_name.lower() / "credentials.json"
            )
            if env_file.exists():
                env_file.unlink()
        except IOError:
            success = False

            self._used_backend = None
        return success
