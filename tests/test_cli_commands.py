import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest


class TestCLICommands:
    """Test suite for CLI commands (init, reset)."""

    @pytest.fixture
    def temp_vault_dir(self):
        """Create a temporary directory for vault files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_getpass(self):
        """Mock getpass to avoid real password prompts in tests."""
        with patch("getpass.getpass") as mock:
            yield mock

    @pytest.fixture
    def mock_input(self):
        """Mock input for user confirmation prompts."""
        with patch("builtins.input") as mock:
            yield mock

    def test_handle_init_command_success(self, temp_vault_dir, mock_getpass):
        """Test successful vault initialization."""
        # Import here to avoid circular imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from lox import handle_init_command

        # Mock Vault
        with patch("lox.Vault") as mock_vault_class:
            mock_vault = MagicMock()
            mock_vault.vault_exists.return_value = False
            mock_vault.initialize_vault.return_value = True
            mock_vault_class.return_value = mock_vault

            # Mock getpass
            mock_getpass.side_effect = ["test_password", "test_password"]

            # Capture print output
            with patch("builtins.print") as mock_print:
                handle_init_command()

                # Verify vault was initialized
                mock_vault.initialize_vault.assert_called_once_with("test_password")

                # Check that success message was printed
                success_calls = [
                    str(call)
                    for call in mock_print.call_args_list
                    if "success" in str(call).lower()
                ]
                assert len(success_calls) > 0, "Success message not found"

    def test_handle_init_command_vault_exists(self, temp_vault_dir):
        """Test init when vault already exists."""
        from lox import handle_init_command

        with patch("lox.Vault") as mock_vault_class:
            mock_vault = MagicMock()
            mock_vault.vault_exists.return_value = True
            mock_vault_class.return_value = mock_vault

            with patch("builtins.print") as mock_print:
                handle_init_command()

                # Verify vault was not initialized
                mock_vault.initialize_vault.assert_not_called()

                # Check that vault exists message was printed
                vault_calls = [
                    str(call)
                    for call in mock_print.call_args_list
                    if "vault" in str(call).lower() and "exists" in str(call).lower()
                ]
                assert len(vault_calls) > 0, "Vault exists message not found"

    def test_handle_init_command_password_mismatch(self, temp_vault_dir, mock_getpass):
        """Test init with password mismatch."""
        from lox import handle_init_command

        with patch("lox.Vault") as mock_vault_class:
            mock_vault = MagicMock()
            mock_vault.vault_exists.return_value = False
            mock_vault_class.return_value = mock_vault

            # Mock getpass to return mismatched passwords
            mock_getpass.side_effect = [
                "password1",
                "password2",
                "test_password",
                "test_password",
            ]

            with patch("builtins.print") as mock_print:
                handle_init_command()

                # Check that password mismatch message was printed
                mismatch_calls = [
                    str(call)
                    for call in mock_print.call_args_list
                    if "match" in str(call).lower()
                ]
                assert len(mismatch_calls) > 0, "Password mismatch message not found"

                # Verify vault was eventually initialized
                mock_vault.initialize_vault.assert_called_once_with("test_password")

    def test_handle_init_command_empty_password(self, temp_vault_dir, mock_getpass):
        """Test init with empty password."""
        from lox import handle_init_command

        with patch("lox.Vault") as mock_vault_class:
            mock_vault = MagicMock()
            mock_vault.vault_exists.return_value = False
            mock_vault_class.return_value = mock_vault

            # Mock getpass to return empty password first, then valid ones
            mock_getpass.side_effect = ["", "test_password", "test_password"]

            with patch("builtins.print") as mock_print:
                handle_init_command()

                # Check that empty password message was printed
                empty_calls = [
                    str(call)
                    for call in mock_print.call_args_list
                    if "empty" in str(call).lower()
                ]
                assert len(empty_calls) > 0, "Empty password message not found"

                # Verify vault was initialized with correct password
                mock_vault.initialize_vault.assert_called_once_with("test_password")

    def test_handle_reset_command_no_vault(self):
        """Test reset when no vault exists."""
        from lox import handle_reset_command

        with patch("lox.Vault") as mock_vault_class:
            mock_vault = MagicMock()
            mock_vault.vault_exists.return_value = False
            mock_vault_class.return_value = mock_vault

            with patch("builtins.print") as mock_print:
                handle_reset_command()

                # Check that no vault message was printed
                no_vault_calls = [
                    str(call)
                    for call in mock_print.call_args_list
                    if "vault" in str(call).lower() and "exist" in str(call).lower()
                ]
                assert len(no_vault_calls) > 0, "No vault message not found"

    def test_handle_reset_command_cancelled(self, mock_input):
        """Test reset command cancellation."""
        from lox import handle_reset_command

        with patch("lox.Vault") as mock_vault_class:
            mock_vault = MagicMock()
            mock_vault.vault_exists.return_value = True
            mock_vault_class.return_value = mock_vault

            # Mock user cancellation
            mock_input.return_value = "n"

            with patch("builtins.print") as mock_print:
                handle_reset_command()

                # Verify cancellation message was printed
                cancel_calls = [
                    str(call)
                    for call in mock_print.call_args_list
                    if "cancel" in str(call).lower()
                ]
                assert len(cancel_calls) > 0, "Cancellation message not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
