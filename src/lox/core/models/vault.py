"""Data models for vault structure."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Credential:
    """Represents a stored credential for a service."""

    password: str
    username: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)


@dataclass
class VaultData:
    """Represents the complete vault data structure."""

    services: Dict[str, Credential] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(
        default_factory=lambda: {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "services": {
                name: {
                    "password": cred.password,
                    "username": cred.username,
                    "url": cred.url,
                    "notes": cred.notes,
                    "created": cred.created.isoformat(),
                    "updated": cred.updated.isoformat(),
                }
                for name, cred in self.services.items()
            },
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VaultData":
        """Create from dictionary."""
        vault_data = cls()
        vault_data.metadata = data.get("metadata", {})

        for name, cred_data in data.get("services", {}).items():
            vault_data.services[name] = Credential(
                password=cred_data.get("password", ""),
                username=cred_data.get("username"),
                url=cred_data.get("url"),
                notes=cred_data.get("notes"),
                created=datetime.fromisoformat(
                    cred_data.get("created", datetime.now().isoformat())
                ),
                updated=datetime.fromisoformat(
                    cred_data.get("updated", datetime.now().isoformat())
                ),
            )

        return vault_data
