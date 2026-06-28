"""JWT / Bearer Token reference implementation."""

from identity_mapper.providers.jwt.capabilities import (
    JwtAuthenticationError,
    JwtAuthenticator,
    JwtCredentialVerifier,
    JwtIdentityResolver,
)
from identity_mapper.providers.jwt.domain import (
    JwtConfig,
    JwtRecord,
    JwtRequest,
)
from identity_mapper.providers.jwt.mapper import (
    JwtCandidateMapper,
    JwtIdentityMapper,
    JwtMapper,
    JwtResolution,
)
from identity_mapper.providers.jwt.provider import InMemoryJwtStore

__all__ = [
    "InMemoryJwtStore",
    "JwtAuthenticationError",
    "JwtAuthenticator",
    "JwtCandidateMapper",
    "JwtConfig",
    "JwtCredentialVerifier",
    "JwtIdentityMapper",
    "JwtIdentityResolver",
    "JwtMapper",
    "JwtRecord",
    "JwtRequest",
    "JwtResolution",
]
