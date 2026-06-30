from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class OAuthConfig:
    """Configuration for the OAuth implementation."""

    realm: str | None = None
    credential_type: str = "BEARER_TOKEN"


@dataclass(frozen=True, slots=True)
class OAuthTargetProjectionConfig:
    """Configuration for projecting an Identity into an OAuth target world."""

    provider: str = "oauth"
    default_issuer: str | None = None
    default_audience: str | None = None


@dataclass(frozen=True, slots=True)
class OAuthTokenRequest:
    """Implementation model for an OAuth token authentication request."""

    subject: str
    access_token: str = field(repr=False)
    issuer: str | None = None
    audience: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class OAuthTokenRecord:
    """Implementation model for an OAuth token introspection record."""

    token_id: str
    subject: str
    access_token: str = field(repr=False)
    identity_id: str
    active: bool = True
    display_name: str | None = None
    email: str | None = None
    scopes: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
