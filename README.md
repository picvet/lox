# Lox

A secure and simple command-line password manager built with Python.

## Features

* Secure AES-256 encryption for your password vault.

* Generate strong, random passwords.

* Retrieve and copy passwords to your clipboard.

* Simple CLI interface.

## Installation

1. Clone the repository:

``` bash
git clone https://github.com/picvet/lox.git
cd lox
```

2. Set up a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
Lox is a command-line tool. Begin by initializing your vault, then add and retrieve credentials as needed.

### 1. Initialize the vault
This command creates a new encrypted password vault.

```bash
python3 lox.py init
```
### 2. Add a new password
Add a new password for a service, optionally generating a custom password.

```bash
python3 lox.py add --name github
```
You can also specify password generation options:

```bash
python3 lox.py add --name google --length 24 --no-symbols
```
### 3. Retrieve a password
Retrieve a password for a service and copy it to your clipboard.

```bash
python3 lox.py get --name github
```
### 4. List all services 
Show all stored service names.

```bash
python3 lox.py list 
```
### 4. Delete a service 
Remove a service from the vault.
```bash
python3 lox.py delete --name github
```
### 6. Reset the vault
This command permanently deletes all data from your vault.

```bash
python3 lox.py reset
```

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
