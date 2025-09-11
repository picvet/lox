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
