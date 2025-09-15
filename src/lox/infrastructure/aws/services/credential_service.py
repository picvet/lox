"""AWS credential management service with secure storage."""

import getpass
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple

import keyring
from keyring.errors import KeyringError

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    KEYRING = "keyring"
    ENV_FILE = "env_file"


class AWSCredentialError(Exception):
    """Exception for AWS credential-related errors."""

    pass


class AWSCredentialService:
    """Service for managing AWS credentials with secure storage."""

    def __init__(self, service_name: str = "LoxPasswordManager"):
        self.service_name = service_name
        self._used_backend: Optional[StorageBackend] = None
        self._backend_preference = [StorageBackend.KEYRING, StorageBackend.ENV_FILE]

    def prompt_for_credentials(self) -> Dict[str, str]:
        """
        Prompts the user for AWS credentials with input validation.
        """
        try:
            role_arn = input("Enter role arn: ").strip()
            if not role_arn:
                raise ValueError("Role arn cannot be empty")

            access_key = input("Enter access key: ").strip()
            if not access_key:
                raise ValueError("Access key cannot be empty")

            secret_key = input("Enter secret key: ").strip()
            if not secret_key:
                raise ValueError("Secret key cannot be empty")

            region = input("Enter region of DynamoDB: ").strip()
            if not region:
                raise ValueError("DynamoDB region cannot be empty")

            return {
                "role_arn": role_arn,
                "access_key": access_key,
                "secret_key": secret_key,
                "region": region,
            }

        except ValueError as e:
            print(f"❌ Validation error: {e}")
            raise

    def store_credentials(self, credentials: Dict[str, str]) -> bool:
        """
        Store AWS credentials using the most secure available backend.

        Args:
            credentials: Dictionary containing AWS credentials

        Returns:
            bool: True if storage successful

        Raises:
            AWSCredentialError: If all storage methods fail
        """
        credential_data = credentials.copy()

        for backend in self._backend_preference:
            try:
                if self._store_with_backend(backend, credential_data):
                    self._used_backend = backend
                    logger.info("Credentials stored using %s backend", backend.value)
                    return True
            except Exception as e:
                logger.warning("Storage with %s failed: %s", backend.value, e)
                continue

        raise AWSCredentialError("All credential storage methods failed")

    def retrieve_credentials(self) -> Optional[Dict[str, str]]:
        """
        Retrieve stored AWS credentials.

        Returns:
            Optional[Dict]: Stored credentials or None if not found
        """
        for backend in self._backend_preference:
            try:
                creds = self._retrieve_from_backend(backend)
                if creds:
                    return creds
            except Exception as e:
                logger.debug("Retrieval from %s failed: %s", backend.value, e)
                continue

        return None

    def clear_credentials(self) -> bool:
        """Remove stored credentials from all backends."""
        success = True

        try:
            user = getpass.getuser()
            keyring.delete_password(f"{self.service_name}-credentials", user)
        except KeyringError:
            success = False

        try:
            env_file = self._get_env_file_path()
            if env_file.exists():
                env_file.unlink()
        except OSError:
            success = False

        self._used_backend = None
        return success

    def _store_with_backend(self, backend: StorageBackend, data: Dict) -> bool:
        """Store credentials using specific backend."""
        methods = {
            StorageBackend.KEYRING: self._store_keyring,
            StorageBackend.ENV_FILE: self._store_env_file,
        }
        return methods[backend](data)

    def _retrieve_from_backend(self, backend: StorageBackend) -> Optional[Dict]:
        """Retrieve credentials from specific backend."""
        methods = {
            StorageBackend.KEYRING: self._retrieve_keyring,
            StorageBackend.ENV_FILE: self._retrieve_env_file,
        }
        return methods[backend]()

    def _store_keyring(self, data: Dict) -> bool:
        """Store credentials in system keyring."""
        try:
            user = getpass.getuser()
            keyring.set_password(
                f"{self.service_name}-credentials", user, json.dumps(data)
            )
            return True
        except KeyringError as e:
            logger.debug("Keyring storage failed: %s", e)
            return False

    def _retrieve_keyring(self) -> Optional[Dict]:
        """Retrieve credentials from system keyring."""
        try:
            user = getpass.getuser()
            creds_json = keyring.get_password(f"{self.service_name}-credentials", user)

            if creds_json:
                return json.loads(creds_json)
        except (KeyringError, json.JSONDecodeError) as e:
            logger.debug("Keyring retrieval failed: %s", e)

        return None

    def _store_env_file(self, data: Dict) -> bool:
        """Store credentials in environment file."""
        try:
            env_file = self._get_env_file_path()
            env_file.parent.mkdir(parents=True, exist_ok=True)

            env_file.write_text(json.dumps(data, indent=2))
            env_file.chmod(0o600)  # Restrict permissions
            return True
        except OSError as e:
            logger.debug("Env file storage failed: %s", e)
            return False

    def _retrieve_env_file(self) -> Optional[Dict]:
        """Retrieve credentials from environment file."""
        try:
            env_file = self._get_env_file_path()
            if env_file.exists():
                return json.loads(env_file.read_text())
        except (OSError, json.JSONDecodeError) as e:
            logger.debug("Env file retrieval failed: %s", e)

        return None

    def _get_env_file_path(self) -> Path:
        """Get path to environment credentials file."""
        return Path.home() / ".config" / self.service_name.lower() / "credentials.json"
