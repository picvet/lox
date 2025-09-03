import pytest

from core.storage import Vault


class TestStorageIntegration:
    """Integration tests for storage functionality."""

    @pytest.fixture
    def test_vault(self, tmp_path):
        """Create a test vault in temporary directory."""
        vault_path = tmp_path / "test_vault.enc"
        return Vault(str(vault_path))

    def test_vault_initialization(self, test_vault):
        """Test vault initialization."""
        assert not test_vault.vault_exists()

        success = test_vault.initialize_vault("master_password_123")
        assert success == True
        assert test_vault.vault_exists()

    def test_vault_save_and_load(self, test_vault):
        """Test saving and loading vault data."""
        # Initialize first
        test_vault.initialize_vault("master_password_123")

        test_data = {
            "services": {
                "github": {"username": "user1", "password": "gh_secret_123"},
                "email": {
                    "username": "user@example.com",
                    "password": "email_secret_456",
                },
            },
            "metadata": {"version": "1.0", "created": "2024-01-01"},
        }

        # Save data
        success = test_vault.save_vault(test_data, "master_password_123")
        assert success == True

        # Load data
        loaded_data = test_vault.load_vault("master_password_123")
        assert loaded_data == test_data

    def test_vault_wrong_password(self, test_vault):
        """Test vault rejection of wrong password."""
        test_vault.initialize_vault("master_password_123")

        test_data = {"services": {"test": {"password": "secret"}}}
        test_vault.save_vault(test_data, "master_password_123")

        # Try wrong password
        with pytest.raises(Exception, match="master password may be incorrect"):
            test_vault.load_vault("wrong_password")

    def test_vault_corruption_detection(self, test_vault):
        """Test vault detection of corrupted files."""
        test_vault.initialize_vault("master_password_123")

        test_data = {"services": {"test": {"password": "secret"}}}
        test_vault.save_vault(test_data, "master_password_123")

        # Corrupt the file
        with open(test_vault.vault_path, "ab") as f:
            f.write(b"garbage_data")

        # Should detect corruption
        with pytest.raises(Exception, match="Failed to decrypt"):
            test_vault.load_vault("master_password_123")
