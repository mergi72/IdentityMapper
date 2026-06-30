from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class MfaConfig:
    """Configuration for the MFA implementation."""

    realm: str | None = None
    credential_type: str = "MFA_FACTORS"


@dataclass(frozen=True, slots=True)
class MfaTargetProjectionConfig:
    """Configuration for projecting an Identity into an MFA target world."""

    provider: str = "mfa"
    default_realm: str | None = None


@dataclass(frozen=True, slots=True)
class MfaFactor:
    """Implementation model for one MFA factor."""

    type: str
    value: str = field(repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MfaRequest:
    """Implementation model for an MFA authentication request."""

    identifier: str
    factors: tuple[MfaFactor, ...]
    realm: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MfaRecord:
    """Implementation model for an MFA identity record."""

    implementation_id: str
    identifier: str
    required_factors: dict[str, str] = field(repr=False)
    identity_id: str
    active: bool = True
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
