from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ApiKeyConfig:
    """Configuration for the API Key implementation."""

    realm: str | None = None
    credential_type: str = "API_KEY"


@dataclass(frozen=True, slots=True)
class ApiKeyTargetProjectionConfig:
    """Configuration for projecting an Identity into an API Key target world."""

    provider: str = "api_key"
    default_client_id: str | None = None


@dataclass(frozen=True, slots=True)
class ApiKeyRequest:
    """Implementation model for an API key authentication request."""

    key_id: str
    api_key: str = field(repr=False)
    client_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ApiKeyRecord:
    """Implementation model for an API key record."""

    key_id: str
    api_key: str = field(repr=False)
    identity_id: str
    active: bool = True
    client_id: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
