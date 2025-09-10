from core.credential_manager import CredentialManager


def setup_aws_credentials():
    """Interactive AWS credentials setup"""
    print("🔐 AWS Credentials Setup for Lox Password Manager")
    print("=" * 50)

    aws_access_key = input("Enter AWS Access Key ID: ")
    aws_secret_key = input("Enter AWS Secret Access Key: ")
    region = input("Enter AWS Region (default: us-east-1): ") or "us-east-1"

    if store_credentials_securely(aws_access_key, aws_secret_key, region):
        print("✅ Credentials stored securely!")
        print("\nNext steps:")
        print("1. Run 'lox sync test' to verify connection")
        print("2. Credentials will be valid for 7 days")
    else:
        print("❌ Failed to store credentials")


def store_credentials_securely(access_key, secret_key, region):
    """Store credentials using platform-specific secure storage"""
    try:
        return CredentialManager()._store_linux(access_key, secret_key, region)
    except Exception as e:
        print(f"Warning: Secure storage failed: {e}")
