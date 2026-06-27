from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class JwtConfig:
    """Configuration for the JWT / Bearer Token implementation."""

    realm: str | None = None
    credential_type: str = "BEARER_TOKEN"


@dataclass(frozen=True, slots=True)
class JwtRequest:
    """Implementation model for a JWT / Bearer Token authentication request."""

    subject: str
    bearer_token: str = field(repr=False)
    issuer: str | None = None
    audience: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class JwtRecord:
    """Implementation model for a decoded JWT / Bearer Token record."""

    jwt_id: str
    subject: str
    bearer_token: str = field(repr=False)
    identity_id: str
    active: bool = True
    issuer: str | None = None
    audience: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
