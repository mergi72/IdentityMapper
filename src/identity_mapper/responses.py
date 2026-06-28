from dataclasses import dataclass

from identity_mapper.domain import Identity, IdentityCandidate


@dataclass(frozen=True, slots=True)
class AuthenticateResponse:
    """Response produced by the Authenticate capability."""

    authenticated: bool
    identity: Identity | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ResolveIdentityResponse:
    """Response produced by the ResolveIdentity capability."""

    candidate: IdentityCandidate | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class VerifyCredentialResponse:
    """Response produced by the VerifyCredential capability."""

    verified: bool
    error: str | None = None
