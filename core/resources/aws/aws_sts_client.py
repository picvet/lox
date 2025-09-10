import boto3

from scripts import store_credentials_securely


class AWSSecurityManager:
    def __init__(self):
        self.sts_client = boto3.client("sts")

    def get_temporary_credentials(self, duration_hours=168):
        """Get temporary credentials that auto-expire"""
        try:
            response = self.sts_client.get_session_token(
                DurationSeconds=duration_hours * 3600,
            )

            creds = response["Credentials"]
            return {
                "access_key": creds["AccessKeyId"],
                "secret_key": creds["SecretAccessKey"],
                "session_token": creds["SessionToken"],
                "expiration": creds["expiration"],
            }
        except Exception as e:
            print(f"Failed to get temporary credentials: {e}")
            return None

    def setup_secure_credentials(self):
        """Guide user through secure setup"""
        print("🔐 Secure AWS Setup")
        print("=" * 50)
        print("1. Create an IAM user with DynamoDB access")
        print("2. Generate access keys in AWS Console")
        print("3. We'll store temporary credentials for 7 days")
        print("4. Credentials will auto-expire for security")

        access_key = input("AWS Access Key ID:")
        secret_key = input("AWS Secret Access Key:")

        # Exchange for temporary credentials
        temp_creds = self.get_temporary_credentials()
        if temp_creds:
            # Store the temporary credentials securely
            store_credentials_securely(
                temp_creds[access_key],
                temp_creds[secret_key],
                temp_creds["session_token"],
                "us_east-1",
            )
            print(
                f"✅ Temporary credentials valid until: {
                  temp_creds['expiration']}"
            )
