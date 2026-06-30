from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class WebAuthnConfig:
    """Configuration for the WebAuthn / FIDO2 implementation."""

    realm: str | None = None
    credential_type: str = "WEBAUTHN_ASSERTION"


@dataclass(frozen=True, slots=True)
class WebAuthnTargetProjectionConfig:
    """Configuration for projecting an Identity into a WebAuthn target world."""

    provider: str = "webauthn"
    default_relying_party_id: str | None = None


@dataclass(frozen=True, slots=True)
class WebAuthnRequest:
    """Implementation model for a WebAuthn authentication request."""

    credential_id: str
    assertion: str = field(repr=False)
    user_handle: str | None = None
    relying_party_id: str | None = None
    challenge: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WebAuthnCredentialRecord:
    """Implementation model for a registered WebAuthn credential."""

    credential_id: str
    assertion: str = field(repr=False)
    identity_id: str
    active: bool = True
    user_handle: str | None = None
    relying_party_id: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
