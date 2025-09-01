# Lox

A secure and simple command-line password manager built with Python.

## Features (Planned)

*   Secure AES-256 encryption for your password vault.
*   Generate strong, random passwords.
*   Copy passwords directly to your clipboard.
*   Simple CLI interface.

## Installation

1.  Clone the repository:
    ```bash
    git clone <your-github-repo-url>
    cd lox
    ```

2.  Set up a virtual environment and install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

## Usage
# Example usage
master_password = "my_secure_password_123"
data_to_encrypt = '{"github": {"username": "user", "password": "secret123"}}'

# Derive key and encrypt
key, salt = derive_key(master_password)
encrypted = encrypt_data(data_to_encrypt, key)

# Decrypt (using same salt)
key2, _ = derive_key(master_password, salt)
decrypted = decrypt_data(encrypted, key2)

print(f"Original: {data_to_encrypt}")
print(f"Decrypted: {decrypted}")
print(f"Match: {data_to_encrypt == decrypted}")

