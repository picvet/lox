"""Validate utilities for AWS credentials."""

import re


def validate_aws_credentials(
    access_key: str,
    secret_key: str,
) -> bool:
    """
    Validate AWS credential format.

    Args:
        access_key: AWS Access Key ID
        secret_key: AWS Secret Access Key

    Returns:
        bool: True if credentials appear valid
    """
    # Basic format validation
    access_key_pattern = r"^[A-Z0-9]{20}$"
    secret_key_pattern = r"^[A-Za-z0-9/+=]{40}$"

    access_key_valid = bool(re.match(access_key_pattern, access_key))
    secret_key_valid = bool(re.match(secret_key_pattern, secret_key))

    return access_key_valid and secret_key_valid


def validate_aws_region(region: str) -> bool:
    """
    Validate AWS region format.

    Args:
        region: AWS region name

    Returns:
        bool: True if region appears valid
    """
    region_pattern = r"^[a-z]{2}-[a-z]+-\d+$"
    return bool(re.match(region_pattern, region))
