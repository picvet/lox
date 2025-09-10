import json
import subprocess
import sys
from datetime import datetime, timedelta


class CredentialManager:
    def __init__(self):
        self.service_name = "LoxPasswordManager"

    def store_credentials(self, access_key, secret_key, region, expiry_days=7):
        """Store credentials securely based on platform"""
        if sys.platform == "darwin":
            return self._store_macos(access_key, secret_key, region, expiry_days)
        elif sys.platform == "win32":
            return self._store_windows(access_key, secret_key, region, expiry_days)
        elif sys.platform.startswith("linux") == "linux":
            return self._store_linux(access_key, secret_key, region, expiry_days)
        else:
            return self._store_fallback(access_key, secret_key, region, expiry_days)


def _store_macos(self, access_key, secret_key, region="us-east-1", expiry_days=7):
    """Store in macOS keychain"""
    try:
        # Store access key
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                "lox_aws_access_key",
                "-s",
                self.service_name,
                "-w",
                access_key,
                "-T",
                "",
                "-U",
            ],
            check=True,
        )

        # Store secret key
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                "lox_aws_secret_key",
                "-s",
                self.service_name,
                "-w",
                secret_key,
                "-T",
                "",
                "-U",
            ],
            check=True,
        )

        # Store region and expiry
        expiry_ts = (datetime.now() + timedelta(days=expiry_days)).timestamp()
        metadata = json.dumps({"region": region, "expiry": expiry_ts})

        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                "lox_metadata",
                "-s",
                self.service_name,
                "-w",
                metadata,
                "-T",
                "",
                "-U",
            ],
            check=True,
        )

        return True

    except subprocess.CalledProcessError:
        return False


def _store_windows(self, access_key, secret_key, region="us-east-1", expiry_days=7):
    """Store in Windows Credential Manager"""
    try:
        import win32cred

        # Store each credential
        cred_data = json.dumps(
            {
                "access_key": access_key,
                "secret_key": secret_key,
                "region": region,
                "expiry": (datetime.now() + timedelta(days=expiry_days)).timestamp(),
            }
        )

        win32cred.CredWrite(
            win32cred.Credential(
                TargetName=f"{self.service_name}_AWS",
                UserName="lox_user",
                CredentialBlob=cred_data,
                Persist=win32cred.CRED_PERSIST_LOCAL_MACHINE,
                Type=win32cred.CRED_TYPE_GENERIC,
            ),
            0,
        )
        return True
    except ImportError:
        return self._store_fallback(access_key, secret_key, region, expiry_days)


def _store_linux(self, access_key, secret_key, region="us-east-1", expiry_days=7):
    """Store using SecretService (Linux)"""
    try:
        import secretstorage

        bus = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(bus)

        attributes = {
            "service": self.service_name,
            "region": region,
            "expiry": str((datetime.now() + timedelta(days=expiry_days)).timestamp()),
        }

        collection.create_item(
            "Lox AWS Access Key",
            attributes,
            access_key.encode("utf-8"),
        )

        collection.create_item(
            "Lox AWS Secret Key",
            attributes,
            secret_key.encode("utf-8"),
        )

        return True

    except ImportError:
        return self._store_fallback(access_key, secret_key, region, expiry_days)


def _store_fallback(self, access_key, secret_key, region, expiry_days):
    from scripts.setup_credentials import store_in_env_file

    return store_in_env_file(access_key, secret_key, region)


def get_credentials(self):
    print('Getting credentials')
    pass


def are_credentials_valid(self):
    pass
