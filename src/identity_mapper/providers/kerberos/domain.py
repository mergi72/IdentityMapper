from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class KerberosConfig:
    """Configuration for the Kerberos implementation."""

    realm: str | None = None
    credential_type: str = "KERBEROS_TICKET"


@dataclass(frozen=True, slots=True)
class KerberosTargetProjectionConfig:
    """Configuration for projecting an Identity into a Kerberos target world."""

    provider: str = "kerberos"
    default_realm: str | None = None


@dataclass(frozen=True, slots=True)
class KerberosRequest:
    """Implementation model for a Kerberos authentication request."""

    principal: str
    ticket: str = field(repr=False)
    realm: str | None = None
    service: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KerberosPrincipalRecord:
    """Implementation model for a Kerberos principal record."""

    principal: str
    ticket: str = field(repr=False)
    identity_id: str
    active: bool = True
    realm: str | None = None
    service: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
