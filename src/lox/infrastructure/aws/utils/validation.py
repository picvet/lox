"""Validation utilities for AWS credentials and resources."""

import re
from typing import Dict, Optional


def validate_aws_credentials(credentials: Dict) -> Optional[str]:
    """
    Validate AWS credentials format.

    Args:
        credentials: Dictionary containing AWS credentials

    Returns:
        Optional[str]: Error message if invalid, None if valid
    """
    if not credentials.get("role_arn"):
        return "Role ARN is required"

    if not credentials.get("access_key"):
        return "Access key is required"

    if not credentials.get("secret_key"):
        return "Secret key is required"

    if not credentials.get("region"):
        return "Region is required"

    if not validate_aws_role_arn(credentials["role_arn"]):
        return "Invalid Role ARN format"

    if not validate_aws_access_key(credentials["access_key"]):
        return "Invalid Access Key format"

    if not validate_aws_secret_key(credentials["secret_key"]):
        return "Invalid Secret Key format"

    if not validate_aws_region(credentials["region"]):
        return "Invalid AWS region"

    return None


def validate_aws_role_arn(role_arn: str) -> bool:
    """Validate AWS Role ARN format."""
    pattern = r"^arn:aws:iam::\d{12}:role/[\w+=,.@-]+$"
    return bool(re.match(pattern, role_arn))


def validate_aws_access_key(access_key: str) -> bool:
    """Validate AWS Access Key ID format."""
    pattern = r"^(AKIA|ASIA)[A-Z0-9]{16}$"
    return bool(re.match(pattern, access_key))


def validate_aws_secret_key(secret_key: str) -> bool:
    """Validate AWS Secret Access Key format."""
    pattern = r"^[A-Za-z0-9/+=]{40}$"
    return bool(re.match(pattern, secret_key))


def validate_aws_region(region_name: str) -> bool:
    """Validate AWS region name format."""
    pattern = r"^[a-z]{2}-[a-z]+-\d+$"
    return bool(re.match(pattern, region_name))
