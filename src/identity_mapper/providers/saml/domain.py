from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SamlConfig:
    """Configuration for the SAML implementation."""

    realm: str | None = None
    credential_type: str = "SAML_ASSERTION"


@dataclass(frozen=True, slots=True)
class SamlTargetProjectionConfig:
    """Configuration for projecting an Identity into a SAML target world."""

    provider: str = "saml"
    default_issuer: str | None = None
    default_audience: str | None = None


@dataclass(frozen=True, slots=True)
class SamlRequest:
    """Implementation model for a SAML authentication request."""

    name_id: str
    assertion: str = field(repr=False)
    issuer: str | None = None
    audience: str | None = None
    session_index: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SamlAssertionRecord:
    """Implementation model for a SAML assertion record."""

    assertion_id: str
    name_id: str
    assertion: str = field(repr=False)
    identity_id: str
    active: bool = True
    issuer: str | None = None
    audience: str | None = None
    session_index: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
