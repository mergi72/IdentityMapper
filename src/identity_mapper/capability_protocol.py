from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
    TargetIdentityResolution,
)


class AuthenticationRejected(Exception):
    """Raised when authentication completes with a rejected result."""


@dataclass(frozen=True, slots=True)
class AuthenticateRequest:
    """Request to execute the Authenticate capability."""

    identification: Identification
    credential: Credential
    provider: str | None = None


@dataclass(frozen=True, slots=True)
class AuthenticateResponse:
    """Response produced by the Authenticate capability."""

    authenticated: bool
    identity: Identity | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ResolveIdentityRequest:
    """Request to execute the ResolveIdentity capability."""

    identification: Identification
    provider: str | None = None


@dataclass(frozen=True, slots=True)
class ResolveIdentityResponse:
    """Response produced by the ResolveIdentity capability."""

    candidate: IdentityCandidate | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class VerifyCredentialRequest:
    """Request to execute the VerifyCredential capability."""

    candidate: IdentityCandidate
    credential: Credential
    provider: str | None = None


@dataclass(frozen=True, slots=True)
class VerifyCredentialResponse:
    """Response produced by the VerifyCredential capability."""

    verified: bool
    error: str | None = None


@dataclass(frozen=True, slots=True)
class MapIdentityRequest:
    """Request to map source identity proof into a target identity world."""

    source_identification: Identification
    source_credential: Credential
    target: IdentityTarget
    source_provider: str | None = None


@dataclass(frozen=True, slots=True)
class MapIdentityResponse:
    """Response produced by the MapIdentity capability."""

    mapped: bool
    identity: Identity | None = None
    target_identity: TargetIdentity | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ResolveTargetIdentityRequest:
    """Request to look up a target identity projection in its target world."""

    target_identity: TargetIdentity


@dataclass(frozen=True, slots=True)
class ResolveTargetIdentityResponse:
    """Response produced by the ResolveTargetIdentity capability."""

    resolved: bool
    resolution: TargetIdentityResolution | None = None
    error: str | None = None


__all__ = [
    "AuthenticationRejected",
    "AuthenticateRequest",
    "AuthenticateResponse",
    "MapIdentityRequest",
    "MapIdentityResponse",
    "ResolveIdentityRequest",
    "ResolveIdentityResponse",
    "ResolveTargetIdentityRequest",
    "ResolveTargetIdentityResponse",
    "VerifyCredentialRequest",
    "VerifyCredentialResponse",
]
