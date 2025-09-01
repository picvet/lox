# tests/test_crypto.py

import pytest
import os
from core.crypto import derive_key, encrypt_data, decrypt_data

class TestCrypto:
    """Test suite for cryptographic functions."""
    
    def test_derive_key_with_salt(self):
        """Test that derive_key generates consistent keys with the same salt."""
        master_password = "secure_master_password_123"
        
        # Derive key with a specific salt
        salt = os.urandom(16)
        key1, used_salt1 = derive_key(master_password, salt)
        key2, used_salt2 = derive_key(master_password, salt)
        
        # Keys should be identical when using the same salt
        assert key1 == key2
        assert used_salt1 == salt
        assert used_salt2 == salt
    
    def test_derive_key_different_salts(self):
        """Test that different salts produce different keys."""
        master_password = "secure_master_password_123"
        
        # Derive keys with different salts
        salt1 = os.urandom(16)
        salt2 = os.urandom(16)
        
        key1, _ = derive_key(master_password, salt1)
        key2, _ = derive_key(master_password, salt2)
        
        # Keys should be different with different salts
        assert key1 != key2
    
    def test_derive_key_generates_salt(self):
        """Test that derive_key generates a salt when none is provided."""
        master_password = "secure_master_password_123"
        
        key1, salt1 = derive_key(master_password)
        key2, salt2 = derive_key(master_password)
        
        # Salts should be different and keys should be different
        assert salt1 != salt2
        assert key1 != key2
        assert len(salt1) == 16  # Salt should be 16 bytes
        assert len(salt2) == 16
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption followed by decryption returns original data."""
        test_data = '{"service": "github", "password": "secret123"}'
        master_password = "master_pass"
        
        # Derive key and encrypt
        key, salt = derive_key(master_password)
        encrypted = encrypt_data(test_data, key)
        
        # Decrypt using the same salt to get same key
        key2, _ = derive_key(master_password, salt)
        decrypted = decrypt_data(encrypted, key2)
        
        assert decrypted == test_data
        assert len(encrypted) > len(test_data)  # Encrypted data should be larger
    
    def test_encrypt_decrypt_wrong_key(self):
        """Test that decryption fails with wrong key."""
        test_data = '{"service": "github", "password": "secret123"}'
        
        # Encrypt with one password
        key1, salt = derive_key("password1")
        encrypted = encrypt_data(test_data, key1)
        
        # Try to decrypt with different password (wrong key)
        key2, _ = derive_key("password2", salt)
        
        with pytest.raises(Exception):  # Should raise some exception
            decrypt_data(encrypted, key2)
    
    def test_encrypt_empty_string(self):
        """Test encryption/decryption of empty string."""
        test_data = ""
        master_password = "master_pass"
        
        key, salt = derive_key(master_password)
        encrypted = encrypt_data(test_data, key)
        
        key2, _ = derive_key(master_password, salt)
        decrypted = decrypt_data(encrypted, key2)
        
        assert decrypted == test_data
    
    def test_encrypt_large_data(self):
        """Test encryption/decryption of larger data."""
        # Create a larger JSON string
        large_data = {'service': 'test', 'data': 'x' * 1000}
        test_data = str(large_data)
        master_password = "master_pass"
        
        key, salt = derive_key(master_password)
        encrypted = encrypt_data(test_data, key)
        
        key2, _ = derive_key(master_password, salt)
        decrypted = decrypt_data(encrypted, key2)
        
        assert decrypted == test_data

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
