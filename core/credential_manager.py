from datetime import datetime, timedelta


class CredentialManager:
    def __init__(self):
        self.service_name = "LoxPasswordManager"

    def store_credentials(self, access_key, secret_key, region, expiry_days=7):
        """Store credentials supports linux only"""
        return self._store_linux(access_key, secret_key, region, expiry_days)

    def _store_linux(self, access_key, secret_key, region="us-east-1", expiry_days=7):
        """Store using SecretService (Linux)"""
        try:
            

        except ImportError:
            return self._store_fallback(access_key, secret_key, region, expiry_days)

    def get_credentials(self):
        print("Getting credentials")
        pass

    def are_credentials_valid(self):
        pass
