"""Passkeys reference implementation."""

from identity_mapper_passkeys.capabilities import (
    PasskeyAuthenticationError,
    PasskeyAuthenticator,
    PasskeyCredentialVerifier,
    PasskeyIdentityResolver,
)
from identity_mapper_passkeys.domain import (
    PasskeyConfig,
    PasskeyRecord,
    PasskeyRequest,
)
from identity_mapper_passkeys.mapper import (
    PasskeyCandidateMapper,
    PasskeyIdentityMapper,
    PasskeyMapper,
    PasskeyResolution,
)
from identity_mapper_passkeys.provider import InMemoryPasskeyStore

__all__ = [
    "InMemoryPasskeyStore",
    "PasskeyAuthenticationError",
    "PasskeyAuthenticator",
    "PasskeyCandidateMapper",
    "PasskeyConfig",
    "PasskeyCredentialVerifier",
    "PasskeyIdentityMapper",
    "PasskeyIdentityResolver",
    "PasskeyMapper",
    "PasskeyRecord",
    "PasskeyRequest",
    "PasskeyResolution",
]
