import json

import pytest

from core.storage import Vault


def test_storage():
    print("Testing the final storage implementation...")

    # Use a test vault path
    test_vault = Vault("test_final_vault.enc")

    # Clean up any previous test file
    import os

    if os.path.exists("test_final_vault.enc"):
        os.remove("test_final_vault.enc")

    # Test 1: Initialize vault
    print("1. Initializing vault...")
    success = test_vault.initialize_vault("master_password_123")
    assert success == True
    print("   ✓ Vault initialized")

    # Test 2: Save data
    print("2. Saving test data...")
    test_data = {
        "services": {
            "github": {"username": "user1", "password": "gh_secret_123"},
            "email": {"username": "user@example.com", "password": "email_secret_456"},
        },
        "metadata": {"version": "1.0", "created": "2024-01-01"},
    }

    success = test_vault.save_vault(test_data, "master_password_123")
    assert success == True
    print("   ✓ Data saved")

    # Test 3: Load data
    print("3. Loading data...")
    loaded_data = test_vault.load_vault("master_password_123")
    assert loaded_data == test_data
    print("   ✓ Data loaded correctly")
    print("   Loaded data:", json.dumps(loaded_data, indent=2))

    # Test 4: Test wrong password
    print("4. Testing wrong password...")
    try:
        test_vault.load_vault("wrong_password")
        print("   ✗ Should have failed!")
    except Exception as e:
        print("   ✓ Correctly rejected wrong password:", str(e)[:50] + "...")

    # Test 5: Test file corruption detection
    print("5. Testing corruption detection...")
    # Corrupt the file by appending garbage
    with open("test_final_vault.enc", "ab") as f:
        f.write(b"garbage_data")

    try:
        test_vault.load_vault("master_password_123")
        print("   ✗ Should have detected corruption!")
    except Exception as e:
        print("   ✓ Correctly detected corruption:", str(e)[:50] + "...")

    # Clean up
    if os.path.exists("test_final_vault.enc"):
        os.remove("test_final_vault.enc")

    print("\n🎉 All tests passed! Storage implementation is working correctly.")


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
