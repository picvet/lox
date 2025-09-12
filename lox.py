import argparse
import sys

from core.handlers import (handle_add_command, handle_delete_command,
                           handle_get_command, handle_init_command,
                           handle_list_command, handle_pull_command,
                           handle_push_command, handle_reset_command)


def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="Lox - A simple CLI password manager", prog="lox"
    )

    # Global arguments that must come BEFORE the subcommand
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="increase output verbosity",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Init command - Create a new vault
    subparsers.add_parser(
        "init",
        help="Initialize a new password vault",
    )

    subparsers.add_parser(
        "setup",
        help="Setup the IAM role for AWS to sync with",
    )

    subparsers.add_parser(
        "push",
        help="Push encrypted vault to DynamoDB, for synching",
    )
    subparsers.add_parser(
        "pull",
        help="Pull encrypted vault from DynamoDB",
    )
    # Reset command - Rest the vault
    subparsers.add_parser(
        "reset",
        help="Reset the vault (deletes all data)",
    )

    # List command - show all stored services
    subparsers.add_parser(
        "list",
        help="List all stored service names",
    )

    # Add command parser
    parser_add = subparsers.add_parser(
        "add",
        help="Add a new credential entry",
    )
    parser_add.add_argument(
        "--name",
        "-n",
        help="Name of the application for this password",
    )
    parser_add.add_argument(
        "--length",
        "-l",
        type=int,
        default=16,
        help="Length of the password (default: 16)",
    )
    parser_add.add_argument(
        "--no-symbols",
        "-ns",
        action="store_false",
        dest="symbols",
        help="Exclude symbols from the password",
    )
    parser_add.add_argument(
        "--no-digits",
        "-nd",
        action="store_false",
        dest="digits",
        help="Exclude digits from the password",
    )
    parser_add.add_argument(
        "--no-uppercase",
        "-nu",
        action="store_false",
        dest="uppercase",
        help="Exclude uppercase letters from the password",
    )

    # Get command parser
    parser_get = subparsers.add_parser(
        "get",
        help="Retrieve a stored credential",
    )
    parser_get.add_argument(
        "--name",
        "-n",
        help="Name of the application",
    )

    # Delete command parser
    parser_delete = subparsers.add_parser(
        "delete",
        help="Deletes a stored credential",
    )
    parser_delete.add_argument(
        "--name",
        "-n",
        help="Name of the application",
    )

    args = parser.parse_args()

    if args.command == "init":
        handle_init_command()
    elif args.command == "reset":
        handle_reset_command()
    elif args.command == "add":
        handle_add_command(args)
    elif args.command == "get":
        handle_get_command(args)
    elif args.command == "delete":
        handle_delete_command(args)
    elif args.command == "list":
        handle_list_command()
    elif args.command == "push":
        handle_push_command()
    elif args.command == "pull":
        handle_pull_command()

    elif args.command == "setup":
        from scripts.setup_credentials import setup_aws_credentials

        setup_aws_credentials()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
