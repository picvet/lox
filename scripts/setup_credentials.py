import sys
from pathlib import Path

from core.credential_manager import _store_linux, _store_macos, _store_windows


def setup_aws_credentials():
    """Interactive AWS credentials setup"""
    print("🔐 AWS Credentials Setup for Lox Password Manager")
    print("=" * 50)

    aws_access_key = input("Enter AWS Access Key ID: ")
    aws_secret_key = input("Enter AWS Secret Access Key: ")
    region = input("Enter AWS Region (default: us-east-1): ") or "us-east-1"

    # Store using platform-specific secure storage
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
        if sys.platform == "darwin":  # macOS
            print('MacOS')
            return _store_macos(access_key, secret_key, region)
        elif sys.platform == "win32":  # Windows
            print('Windows')
            return _store_windows(access_key, secret_key, region)
        elif sys.platform.startswith("linux"):
            print('Linux')
            return _store_linux(access_key, secret_key, region)
        else:
            print('OS not found')
            return store_in_env_file(access_key, secret_key, region)
    except Exception as e:
        print(f"Warning: Secure storage failed: {e}")
        return store_in_env_file(access_key, secret_key, region)


def store_in_env_file(access_key, secret_key, region="us-east-1"):
    env_path = Path.home()
    print(f"Env path: {env_path}")

    encoded_key = access_key.encode("utf-8").hex()
    encoded_secret = secret_key.encode("utf-8").hex()
    encoded_region = region.encode("utf-8").hex()

    with open(f"{env_path}/.env_p", "w") as f:
        f.write(f"LOX_AWS_ACCESS_KEY={encoded_key}\n")
        f.write(f"LOX_AWS_SECRET_KEY={encoded_secret}\n")
        f.write(f"LOX_AWS_REGION={encoded_region}\n")
        f.write(f"LOX_CRED_EXPIRY={7*24*60*60}\n")

    env_path.chmod(0o600)
    return True

