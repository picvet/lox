"""Data models for AWS credentials."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AWSCredentials:
    """Data class representing AWS credentials."""

    role_arn: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    region: Optional[str] = None
    session_token: Optional[str] = None

    def are_complete(self) -> bool:
        """Check if credentials are complete for STS assumption."""
        return all([self.role_arn, self.access_key, self.secret_key, self.region])

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "role_arn": self.role_arn,
            "access_key": self.access_key,
            "secret_key": self.secret_key,
            "region": self.region,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AWSCredentials":
        """Create from dictionary."""
        return cls(
            role_arn=data.get("role_arn"),
            access_key=data.get("access_key"),
            secret_key=data.get("secret_key"),
            region=data.get("region"),
        )
