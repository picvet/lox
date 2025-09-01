#!/usr/bin/env python3
"""
Test runner script for Lox password manager.
Run with: python -m tests.run_tests
"""

import os
import sys

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_tests():
    """Run all tests."""
    print("Running Lox test suite...")
    print("=" * 50)

    # Run tests and exit with appropriate code
    exit_code = pytest.main(["-v", "--tb=short"])

    print("=" * 50)
    if exit_code == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")

    sys.exit(exit_code)


if __name__ == "__main__":
    run_tests()
