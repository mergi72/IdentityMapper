from dataclasses import dataclass

from identity_mapper.domain import Credential, Identification, IdentityCandidate


@dataclass(frozen=True, slots=True)
class AuthenticateRequest:
    """Request to execute the Authenticate capability."""

    provider: str
    identification: Identification
    credential: Credential


@dataclass(frozen=True, slots=True)
class ResolveIdentityRequest:
    """Request to execute the ResolveIdentity capability."""

    provider: str
    identification: Identification


@dataclass(frozen=True, slots=True)
class VerifyCredentialRequest:
    """Request to execute the VerifyCredential capability."""

    provider: str
    candidate: IdentityCandidate
    credential: Credential
