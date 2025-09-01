import argparse

from core.clipboard import copy_to_clipboard
from core.password_gen import generate_password


def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="Lox - A simple CLI password manager", prog="lox"
    )

    # Global arguments that must come BEFORE the subcommand
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Generate command parser
    parser_generate = subparsers.add_parser(
        "generate", help="Generate a new random password"
    )

    parser_generate.add_argument(
        "--name", "-n", help="Name to associate with this password (for saving later)"
    )
    parser_generate.add_argument(
        "--length",
        "-l",
        type=int,
        default=16,
        help="Length of the password (default: 16)",
    )
    parser_generate.add_argument(
        "--no-symbols",
        action="store_false",
        dest="symbols",
        help="Exclude symbols from the password",
    )
    parser_generate.add_argument(
        "--no-digits",
        action="store_false",
        dest="digits",
        help="Exclude digits from the password",
    )
    parser_generate.add_argument(
        "--no-uppercase",
        action="store_false",
        dest="uppercase",
        help="Exclude uppercase letters from the password",
    )
    parser_generate.add_argument(
        "--copy",
        "-c",
        action="store_true",
        help="Copy the generated password to clipboard",
    )

    args = parser.parse_args()

    if args.command == "generate":
        try:
            password = generate_password(
                length=args.length,
                use_symbol=args.symbols,
                use_digits=args.digits,
                use_uppercase=args.uppercase,
            )

            print(f"Generated password: {password}")

            # Copy to clipboard if requested
            if args.copy:
                if copy_to_clipboard(password):
                    print("✓ Copied to clipboard!")
                else:
                    print("✗ Failed to copy to clipboard")

            if args.name and args.verbose:
                print(f"Password generated for: {args.name}")

        except ValueError as e:
            print(f"Error: {e}")
            if args.verbose:
                print("Please check your input parameters and try again.")


if __name__ == "__main__":
    main()
