# Lox

A secure and simple command-line password manager built with Python.

## Features

- **Secure Encryption**: AES-256 encryption for your password vault using industry-standard cryptography
- **Password Generation**: Generate strong, random passwords with customizable options
- **Clipboard Integration**: Retrieve and copy passwords directly to your clipboard
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Simple CLI Interface**: Easy-to-use command-line interface
- **Local Storage**: Your data stays on your machine - no cloud dependencies

## Installation

### From Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/picvet/lox.git
   cd lox
   ```

2. Set up a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  
```

3. Install the package:
```bash
pip install -e .
```

## Usage
Lox is a command-line tool. Begin by initializing your vault, then add and retrieve credentials as needed.

### 1. Initialize the vault
This command creates a new encrypted password vault.

```bash
lox init
```
You'll be prompted to set a master password that will encrypt your vault.

### 2. Add a new password
Add a new password for a service. Lox can generate a strong password for you.

```bash
# Generate a custom password
lox add -n github 

# Password with options
lox add --name google --length 24 --no-symbols
```

### 3. Retrieve a password
Retrieve a password for a service and copy it to your clipboard.

```bash
lox get -n github
```

### 4. List all services 
Show all stored service names.

```bash
lox list 
```

### 5. Delete a service 
Remove a service from the vault.
```bash
lox delete --name github
```
### 6. Reset the vault
This command permanently deletes all data from your vault.

```bash
lox reset
```

### 7. Cloud Sync(Optional) 
Sync your vault with cloud storage (requires additional setup):

```bash
lox setup # configure AWS DynamoDB cloud sync credentials 
lox push  # upload vault to cloud 
lox pull  # download latest vault uploaded from cloud
```

## Security 
- Local Encryption: All data is encrypted locally before storage 
- Master Password: Your master password is never stored - it's used to derive encryption keys 
- No Internet: By default, Lox works entirely offline

## Testing
Lox includes a comprehensive test suite to ensure reliability and security.

### Running Tests Locally
```
# Install test dependencies or install the requirements.txt dependencies and these will be added too
pip install pytest pytest-cov 

# Run all tests with coverate report
python3 -m pytest tests/test_cli.py --cov=./ --cov-report=html

# Run all tests without coverage
python3 -m pytest tests/

```
## Contributing
We welcome contributions! Please feel free to open a pull request or submit an issue.
