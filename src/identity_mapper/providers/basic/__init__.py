"""Basic authentication reference implementation."""

from identity_mapper.providers.basic.capabilities import (
    BasicAuthenticationError,
    BasicAuthenticator,
    BasicCredentialVerifier,
    BasicIdentityResolver,
)
from identity_mapper.providers.basic.domain import BasicAuthConfig, BasicUserRecord
from identity_mapper.providers.basic.mapper import (
    BasicAuthenticationMapper,
    BasicAuthenticationRequest,
    BasicUserCandidateMapper,
    BasicUserIdentityMapper,
    BasicUserResolution,
)
from identity_mapper.providers.basic.provider import InMemoryBasicUserStore

__all__ = [
    "BasicAuthConfig",
    "BasicAuthenticationError",
    "BasicAuthenticationMapper",
    "BasicAuthenticationRequest",
    "BasicAuthenticator",
    "BasicCredentialVerifier",
    "BasicIdentityResolver",
    "BasicUserCandidateMapper",
    "BasicUserIdentityMapper",
    "BasicUserRecord",
    "BasicUserResolution",
    "InMemoryBasicUserStore",
]
