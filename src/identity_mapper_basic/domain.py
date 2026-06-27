from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class BasicAuthConfig:
    """Configuration for the basic authentication implementation."""

    realm: str | None = None
    credential_type: str = "PASSWORD"


@dataclass(frozen=True, slots=True)
class BasicUserRecord:
    """Implementation model for a basic-auth user record."""

    implementation_id: str
    username: str
    password: str = field(repr=False)
    identity_id: str
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
