from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)


class AuthenticationRejected(Exception):
    """Raised when authentication completes with a rejected result."""


@dataclass(frozen=True, slots=True)
class AuthenticateRequest:
    """Request to execute the Authenticate capability."""

    provider: str
    identification: Identification
    credential: Credential


@dataclass(frozen=True, slots=True)
class AuthenticateResponse:
    """Response produced by the Authenticate capability."""

    authenticated: bool
    identity: Identity | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ResolveIdentityRequest:
    """Request to execute the ResolveIdentity capability."""

    provider: str
    identification: Identification


@dataclass(frozen=True, slots=True)
class ResolveIdentityResponse:
    """Response produced by the ResolveIdentity capability."""

    candidate: IdentityCandidate | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class VerifyCredentialRequest:
    """Request to execute the VerifyCredential capability."""

    provider: str
    candidate: IdentityCandidate
    credential: Credential


@dataclass(frozen=True, slots=True)
class VerifyCredentialResponse:
    """Response produced by the VerifyCredential capability."""

    verified: bool
    error: str | None = None


__all__ = [
    "AuthenticationRejected",
    "AuthenticateRequest",
    "AuthenticateResponse",
    "ResolveIdentityRequest",
    "ResolveIdentityResponse",
    "VerifyCredentialRequest",
    "VerifyCredentialResponse",
]
