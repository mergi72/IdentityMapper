from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class GuestConfig:
    """Configuration for the Guest / Anonymous Identity implementation."""

    realm: str | None = "guest"
    credential_type: str = "GUEST_SESSION"


@dataclass(frozen=True, slots=True)
class GuestRequest:
    """Implementation model for a guest identity request."""

    session_id: str
    session_token: str = field(repr=False)
    realm: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GuestSessionRecord:
    """Implementation model for an anonymous guest session."""

    session_id: str
    session_token: str = field(repr=False)
    identity_id: str
    active: bool = True
    display_name: str | None = "Guest"
    roles: tuple[str, ...] = ("guest",)
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
