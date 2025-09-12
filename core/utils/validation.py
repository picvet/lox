"""Validate utilities for AWS credentials."""

import re


def validate_aws_role_arn(
    role_arn: str,
) -> bool:
    """
    Validate AWS credential format.

    Args:
        role_arn: AWS Access Key ID

    Returns:
        bool: True if credentials appear valid
    """
    role_arn_pattern = r"arn:aws:iam::\d{12}:role/[^:]+"

    role_arn_valid = bool(re.match(role_arn_pattern, role_arn))

    return role_arn_valid


def validate_aws_access_key(access_key: str) -> bool:
    """
    Validate AWS Access Key ID.

    Args:
        access_key: AWS Access Key ID

    Returns:
        bool: True if key appears valid
    """
    access_key_pattern = r"^(AKIA|ASIA)[A-Z0-9]{16}$"
    return bool(re.match(access_key_pattern, access_key))


def validate_aws_secret_key(secret_key: str) -> bool:
    """
    Validate AWS Secret Access Key.

    Args:
        secret_key: AWS Secret Access Key

    Returns:
        bool: True if key appears valid
    """
    secret_key_pattern = r"^[A-Za-z0-9/+=]{40}$"
    return bool(re.match(secret_key_pattern, secret_key))
