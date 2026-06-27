"""Guest / Anonymous Identity reference implementation."""

from identity_mapper_guest.capabilities import (
    GuestAuthenticationError,
    GuestAuthenticator,
    GuestCredentialVerifier,
    GuestIdentityResolver,
)
from identity_mapper_guest.domain import (
    GuestConfig,
    GuestRequest,
    GuestSessionRecord,
)
from identity_mapper_guest.mapper import (
    GuestCandidateMapper,
    GuestIdentityMapper,
    GuestMapper,
    GuestResolution,
)
from identity_mapper_guest.provider import InMemoryGuestSessionStore

__all__ = [
    "GuestAuthenticationError",
    "GuestAuthenticator",
    "GuestCandidateMapper",
    "GuestConfig",
    "GuestCredentialVerifier",
    "GuestIdentityMapper",
    "GuestIdentityResolver",
    "GuestMapper",
    "GuestRequest",
    "GuestResolution",
    "GuestSessionRecord",
    "InMemoryGuestSessionStore",
]
