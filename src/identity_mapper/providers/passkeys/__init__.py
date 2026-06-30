"""Passkeys reference implementation."""

from identity_mapper.providers.passkeys.capabilities import (
    PasskeyAuthenticationError,
    PasskeyAuthenticator,
    PasskeyCredentialVerifier,
    PasskeyIdentityResolver,
    PasskeyTargetIdentityMapper,
)
from identity_mapper.providers.passkeys.domain import (
    PasskeyConfig,
    PasskeyRecord,
    PasskeyRequest,
    PasskeyTargetProjectionConfig,
)
from identity_mapper.providers.passkeys.mapper import (
    PasskeyCandidateMapper,
    PasskeyIdentityMapper,
    PasskeyMapper,
    PasskeyResolution,
)
from identity_mapper.providers.passkeys.provider import InMemoryPasskeyStore

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
    "PasskeyTargetIdentityMapper",
    "PasskeyTargetProjectionConfig",
]
