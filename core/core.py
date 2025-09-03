class VaultManager:
    """Manages all interactions with the password vault file."""

    def __init__(self, vault):
        self._vault = vault

    def get_vault_data(self, master_password):
        """Loads and returns vault data, or raises an error on failure."""
        if not self._vault.vault_exists():
            raise FileNotFoundError("No vault exists. Use 'lox init' to create one.")

        try:
            return self._vault.load_vault(master_password)
        except Exception as e:
            raise ValueError(f"Failed to load vault: {e}.")

    def add_password_entry(self, name, password, vault_data):
        """Adds a new password to the vault data."""
        if name in vault_data["services"]:
            raise ValueError(f"'{name}' already exists.")

        vault_data["services"][name] = {"password": password}

    def save_vault_data(self, vault_data, master_password):
        """Saves the updated vault data."""
        return self._vault.save_vault(vault_data, master_password)
