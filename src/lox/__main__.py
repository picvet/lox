import sys

from lox.cli.parser import execute_command


def main():
    """Main entry point for the Lox password manager."""
    from cli.parser import create_parser

    parser, commands = create_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    command = commands.get(args.command)
    if command:
        exit_code = command.run(args)
        sys.exit(exit_code)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
