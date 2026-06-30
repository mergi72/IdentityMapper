from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ClientCertificateConfig:
    """Configuration for the Client Certificate / mTLS implementation."""

    realm: str | None = None
    credential_type: str = "CERTIFICATE_PROOF"


@dataclass(frozen=True, slots=True)
class ClientCertificateTargetProjectionConfig:
    """Configuration for projecting an Identity into a certificate target world."""

    provider: str = "certificate"
    default_issuer: str | None = None


@dataclass(frozen=True, slots=True)
class ClientCertificateRequest:
    """Implementation model for a client certificate authentication request."""

    fingerprint: str
    proof: str = field(repr=False)
    subject: str | None = None
    issuer: str | None = None
    serial_number: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ClientCertificateRecord:
    """Implementation model for a registered client certificate."""

    fingerprint: str
    proof: str = field(repr=False)
    identity_id: str
    active: bool = True
    subject: str | None = None
    issuer: str | None = None
    serial_number: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
