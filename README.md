# Lox

A secure and simple command-line password manager built with Python.

## Features

* Secure AES-256 encryption for your password vault.

* Generate strong, random passwords.

* **Retrieve and copy passwords** to your clipboard.

* Simple CLI interface.

## Installation

1. Clone the repository:

git clone <your-github-repo-url>
cd lox


Set up a virtual environment and install dependencies:

Lox
A secure and simple command-line password manager built with Python.

Features
Secure AES-256 encryption for your password vault.

Generate strong, random passwords.

Retrieve and copy passwords to your clipboard.

Simple CLI interface.

Installation
Clone the repository:

bash
git clone <your-github-repo-url>
cd lox
Set up a virtual environment and install dependencies:

bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
Usage
Lox is a command-line tool. Begin by initializing your vault, then add and retrieve credentials as needed.

1. Initialize the vault
This command creates a new encrypted password vault.

bash
python3 main.py init
2. Add a new password
Add a new password for a service, optionally generating a custom password.

bash
python3 main.py add --name github
You can also specify password generation options:

bash
python3 main.py add --name google --length 24 --no-symbols
3. Retrieve a password
Retrieve a password for a service and copy it to your clipboard.

bash
python3 main.py get --name github
4. Reset the vault
This command permanently deletes all data from your vault.

bash
python3 main.py reset
Contributing
We welcome contributions! Please feel free to open a pull request or submit an issue.
