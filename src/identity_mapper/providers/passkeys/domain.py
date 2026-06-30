from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class PasskeyConfig:
    """Configuration for the Passkeys implementation."""

    realm: str | None = None
    credential_type: str = "PASSKEY_ASSERTION"


@dataclass(frozen=True, slots=True)
class PasskeyTargetProjectionConfig:
    """Configuration for projecting an Identity into a Passkeys target world."""

    provider: str = "passkeys"
    default_relying_party_id: str | None = None


@dataclass(frozen=True, slots=True)
class PasskeyRequest:
    """Implementation model for a passkey authentication request."""

    passkey_id: str
    assertion: str = field(repr=False)
    user_handle: str | None = None
    relying_party_id: str | None = None
    device_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PasskeyRecord:
    """Implementation model for a registered passkey."""

    passkey_id: str
    assertion: str = field(repr=False)
    identity_id: str
    active: bool = True
    user_handle: str | None = None
    relying_party_id: str | None = None
    device_name: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
