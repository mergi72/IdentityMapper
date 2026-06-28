"""Guest / Anonymous Identity reference implementation."""

from identity_mapper.providers.guest.capabilities import (
    GuestAuthenticationError,
    GuestAuthenticator,
    GuestCredentialVerifier,
    GuestIdentityResolver,
)
from identity_mapper.providers.guest.domain import (
    GuestConfig,
    GuestRequest,
    GuestSessionRecord,
)
from identity_mapper.providers.guest.mapper import (
    GuestCandidateMapper,
    GuestIdentityMapper,
    GuestMapper,
    GuestResolution,
)
from identity_mapper.providers.guest.provider import InMemoryGuestSessionStore

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
