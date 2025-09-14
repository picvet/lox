import argparse

from lox.cli.commands import (AddCommand, DeleteCommand, GetCommand,
                              InitCommand, ListCommand, PullCommand,
                              PushCommand, ResetCommand, SetupCommand)


def create_parser():
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Lox - A simple CLI password manager", prog="lox"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    commands = {
        "init": InitCommand(),
        "add": AddCommand(),
        "get": GetCommand(),
        "delete": DeleteCommand(),
        "list": ListCommand(),
        "reset": ResetCommand(),
        "push": PushCommand(),
        "pull": PullCommand(),
        "setup": SetupCommand(),
    }

    for name, command in commands.items():
        subparser = subparsers.add_parser(name, help=command.__doc__)
        command.add_arguments(subparser)

    return parser, commands


def execute_command(command_name: str, args: argparse.Namespace) -> int:
    """Execute the appropriate command."""
    parser, commands = create_parser()
    command = commands.get(command_name)

    if command:
        return command.run(args)
    else:
        print(f"Unknown command: {command_name}")
        return 1
