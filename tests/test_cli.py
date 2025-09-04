# tests/test_cli.py

import sys
from unittest.mock import MagicMock, call, patch

import pytest

from core.handlers import (handle_add_command, handle_delete_command,
                           handle_get_command, handle_init_command,
                           handle_list_command, handle_reset_command)


class TestCLICommands:
    """Test CLI command handlers."""

    # Happy Path Tests

    @patch("core.handlers.Vault")
    @patch("getpass.getpass")
    def test_handle_init_command_success(self, mock_getpass, mock_vault_class):
        """Test successful vault initialization."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = False
        mock_vault.initialize_vault.return_value = True
        mock_vault_class.return_value = mock_vault

        mock_getpass.side_effect = ["password123", "password123"]

        with patch("builtins.print") as mock_print:
            handle_init_command()

            mock_vault.initialize_vault.assert_called_once_with("password123")
            # Check that success message was printed
            assert any(
                "success" in str(call).lower() for call in mock_print.call_args_list
            )

    @patch("core.handlers.Vault")
    def test_handle_init_command_vault_exists(self, mock_vault_class):
        """Test init when vault already exists."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault_class.return_value = mock_vault

        with patch("builtins.print") as mock_print:
            handle_init_command()

            mock_vault.initialize_vault.assert_not_called()
            assert any(
                "exists" in str(call).lower() for call in mock_print.call_args_list
            )

    @patch("core.handlers.Vault")
    @patch("core.handlers.generate_password")
    @patch("core.handlers.copy_to_clipboard")
    @patch("getpass.getpass")
    def test_handle_add_command_success(
        self, mock_getpass, mock_copy, mock_generate, mock_vault_class
    ):
        """Test successful add command."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault.load_vault.return_value = {"services": {}}
        mock_vault.save_vault.return_value = True
        mock_vault_class.return_value = mock_vault

        mock_generate.return_value = "GeneratedPassword123!"
        mock_copy.return_value = True
        mock_getpass.return_value = "master_password"

        args = MagicMock()
        args.name = "github"
        args.length = 16
        args.symbols = True
        args.digits = True
        args.uppercase = True

        with patch("builtins.input", return_value="testuser"), patch(
            "builtins.print"
        ) as mock_print:

            handle_add_command(args)

            # Verify password was generated
            mock_generate.assert_called_once_with(
                length=16, use_symbols=True, use_digits=True, use_uppercase=True
            )
            # Verify vault was loaded and saved
            mock_vault.load_vault.assert_called_once_with("master_password")
            mock_vault.save_vault.assert_called_once()
            # Verify password was copied
            mock_copy.assert_called_once_with("GeneratedPassword123!")
            # Verify success message was printed
            assert any(
                "saved" in str(call).lower() for call in mock_print.call_args_list
            )

    @patch("core.handlers.Vault")
    @patch("getpass.getpass")
    def test_handle_get_command_success(self, mock_getpass, mock_vault_class):
        """Test successful get command."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault.load_vault.return_value = {
            "services": {"github": {"username": "testuser", "password": "secret123"}}
        }
        mock_vault_class.return_value = mock_vault

        mock_getpass.return_value = "master_password"

        args = MagicMock()
        args.name = "github"

        with patch("core.handlers.copy_to_clipboard") as mock_copy, patch(
            "builtins.print"
        ) as mock_print:

            mock_copy.return_value = True
            handle_get_command(args)

            # Verify vault was accessed
            mock_vault.load_vault.assert_called_once_with("master_password")
            # Verify password was copied
            mock_copy.assert_called_once_with("secret123")
            # Verify username was printed
            assert any(
                "Password for" in str(call) for call in mock_print.call_args_list
            )

    @patch("core.handlers.Vault")
    @patch("getpass.getpass")
    def test_handle_list_command_success(self, mock_getpass, mock_vault_class):
        """Test successful list command."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault.load_vault.return_value = {
            "services": {
                "github": {"username": "user1"},
                "email": {"username": "user2"},
            }
        }
        mock_vault_class.return_value = mock_vault

        mock_getpass.return_value = "master_password"

        with patch("builtins.print") as mock_print:
            handle_list_command()

            mock_vault.load_vault.assert_called_once_with("master_password")
            # Verify services were listed
            assert any("github" in str(call) for call in mock_print.call_args_list)
            assert any("email" in str(call) for call in mock_print.call_args_list)

    @patch("core.handlers.Vault")
    @patch("getpass.getpass")
    def test_handle_delete_command_success(self, mock_getpass, mock_vault_class):
        """Test successful delete command."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault.load_vault.return_value = {
            "services": {
                "github": {"username": "testuser", "password": "secret123"},
                "email": {"username": "user@example.com", "password": "email123"},
            }
        }
        mock_vault.save_vault.return_value = True
        mock_vault_class.return_value = mock_vault

        mock_getpass.return_value = "master_password"

        args = MagicMock()
        args.name = "github"

        with patch("builtins.input", return_value="y"), patch(
            "builtins.print"
        ) as mock_print:

            handle_delete_command(args)

            # Verify vault was accessed and saved
            mock_vault.load_vault.assert_called_once_with("master_password")
            mock_vault.save_vault.assert_called_once()
            # Verify success message was printed
            assert any(
                "deleted" in str(call).lower() for call in mock_print.call_args_list
            )

    # Sad Path Tests

    @patch("core.handlers.Vault")
    @patch("getpass.getpass")
    def test_handle_add_command_no_vault(self, mock_getpass, mock_vault_class):
        """Test add command when no vault exists."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = False
        mock_vault_class.return_value = mock_vault

        args = MagicMock()
        args.name = "github"

        with patch("builtins.print") as mock_print:
            handle_add_command(args)

            assert any(
                "exist" in str(call).lower() for call in mock_print.call_args_list
            )
            mock_vault.load_vault.assert_not_called()

    @patch("core.handlers.Vault")
    @patch("getpass.getpass")
    def test_handle_get_command_service_not_found(self, mock_getpass, mock_vault_class):
        """Test get command for non-existent service."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault.load_vault.return_value = {"services": {}}
        mock_vault_class.return_value = mock_vault

        mock_getpass.return_value = "master_password"

        args = MagicMock()
        args.name = "nonexistent"

        with patch("builtins.print") as mock_print:
            handle_get_command(args)

            assert any(
                "not found" in str(call).lower() for call in mock_print.call_args_list
            )

    @patch("core.handlers.Vault")
    @patch("getpass.getpass")
    def test_handle_delete_command_cancelled(self, mock_getpass, mock_vault_class):
        """Test delete command cancellation."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault.load_vault.return_value = {
            "services": {"github": {"username": "testuser"}}
        }
        mock_vault_class.return_value = mock_vault

        mock_getpass.return_value = "master_password"

        args = MagicMock()
        args.name = "github"

        with patch("builtins.input", return_value="n"), patch(
            "builtins.print"
        ) as mock_print:

            handle_delete_command(args)

            mock_vault.save_vault.assert_not_called()  # Should not save
            assert any(
                "cancelled" in str(call).lower() for call in mock_print.call_args_list
            )

    @patch("core.handlers.Vault")
    @patch("getpass.getpass")
    def test_handle_get_command_wrong_password(self, mock_getpass, mock_vault_class):
        """Test get command with wrong password."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault.load_vault.side_effect = Exception("Wrong password")
        mock_vault_class.return_value = mock_vault

        mock_getpass.return_value = "wrong_password"

        args = MagicMock()
        args.name = "github"

        with patch("builtins.print") as mock_print:
            handle_get_command(args)

            assert any(
                "error" in str(call).lower() or "fail" in str(call).lower()
                for call in mock_print.call_args_list
            )

    @patch("core.handlers.Vault")
    def test_handle_reset_command_no_vault(self, mock_vault_class):
        """Test reset command when no vault exists."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = False
        mock_vault_class.return_value = mock_vault

        with patch("builtins.print") as mock_print:
            handle_reset_command()

            assert any(
                "exist" in str(call).lower() for call in mock_print.call_args_list
            )

    @patch("core.handlers.Vault")
    def test_handle_reset_command_cancelled(self, mock_vault_class):
        """Test reset command cancellation."""
        mock_vault = MagicMock()
        mock_vault.vault_exists.return_value = True
        mock_vault_class.return_value = mock_vault

        with patch("builtins.input", return_value="n"), patch(
            "builtins.print"
        ) as mock_print:

            handle_reset_command()

            mock_vault.vault_path = "/tmp/test.enc"  # Mock path
            with patch("os.path.exists", return_value=True), patch(
                "os.remove"
            ) as mock_remove:
                # Should not remove file if cancelled
                handle_reset_command()
                mock_remove.assert_not_called()

            assert any(
                "cancelled" in str(call).lower() for call in mock_print.call_args_list
            )


class TestMainFunction:
    """Test the main function and argument parsing."""

    @patch("lox.handle_init_command")
    def test_main_init_command(self, mock_handler):
        """Test main function with init command."""
        test_args = ["lox", "init"]

        with patch("sys.argv", test_args):
            import lox

            lox.main()

            mock_handler.assert_called_once()

    @patch("lox.handle_add_command")
    def test_main_add_command(self, mock_handler):
        """Test main function with add command."""
        test_args = ["lox", "add", "--name", "github", "--length", "20"]

        with patch("sys.argv", test_args):
            import lox

            lox.main()

            mock_handler.assert_called_once()

    @patch("lox.handle_get_command")
    def test_main_get_command(self, mock_handler):
        """Test main function with get command."""
        test_args = ["lox", "get", "--name", "github"]

        with patch("sys.argv", test_args):
            import lox

            lox.main()

            mock_handler.assert_called_once()

    def test_main_keyboard_interrupt(self):
        """Test main function handling KeyboardInterrupt."""
        with patch("sys.argv", ["lox", "init"]), patch(
            "lox.handle_init_command", side_effect=KeyboardInterrupt
        ), patch("builtins.print") as mock_print:

            import lox

            lox.main()

            assert any(
                "cancelled" in str(call).lower() for call in mock_print.call_args_list
            )
