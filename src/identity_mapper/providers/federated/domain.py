from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class FederatedConfig:
    """Configuration for the Federated Identity implementation."""

    realm: str | None = None
    credential_type: str = "FEDERATION_ASSERTION"


@dataclass(frozen=True, slots=True)
class FederatedTargetProjectionConfig:
    """Configuration for projecting an Identity into a Federated target world."""

    provider: str = "federated"
    default_issuer: str | None = None
    default_audience: str | None = None


@dataclass(frozen=True, slots=True)
class FederatedRequest:
    """Implementation model for a federated identity request."""

    issuer: str
    external_subject: str
    assertion: str = field(repr=False)
    audience: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FederatedIdentityRecord:
    """Implementation model for a trusted federated identity mapping."""

    trust_mapping_id: str
    issuer: str
    external_subject: str
    assertion: str = field(repr=False)
    identity_id: str
    active: bool = True
    audience: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
