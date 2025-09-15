"""AWS infrastructure components for Lox password manager."""

from lox.infrastructure.aws.exceptions import CredentialSetupError
from lox.infrastructure.aws.services.credential_service import (
    AWSCredentialError, AWSCredentialService)
from lox.infrastructure.aws.services.dynamodb_service import (
    DynamoDBService, DynamoDBServiceError)
from lox.infrastructure.aws.services.sts_service import (STSAssumptionError,
                                                         STSService)
from lox.infrastructure.aws.utils.validation import validate_aws_credentials

__all__ = [
    "AWSCredentialService",
    "AWSCredentialError",
    "STSService",
    "STSAssumptionError",
    "DynamoDBService",
    "DynamoDBServiceError",
    "validate_aws_credentials",
    "CredentialSetupError",
]
