"""Basic authentication reference implementation."""

from identity_mapper_basic.capabilities import (
    BasicAuthenticationError,
    BasicAuthenticator,
    BasicCredentialVerifier,
    BasicIdentityResolver,
)
from identity_mapper_basic.domain import BasicAuthConfig, BasicUserRecord
from identity_mapper_basic.mapper import (
    BasicAuthenticationMapper,
    BasicAuthenticationRequest,
    BasicUserCandidateMapper,
    BasicUserIdentityMapper,
    BasicUserResolution,
)
from identity_mapper_basic.provider import InMemoryBasicUserStore

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
