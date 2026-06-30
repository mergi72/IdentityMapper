"""Multi-factor authentication reference implementation."""

from identity_mapper.providers.mfa.capabilities import (
    MfaAuthenticationError,
    MfaAuthenticator,
    MfaCredentialVerifier,
    MfaIdentityResolver,
    MfaTargetIdentityMapper,
)
from identity_mapper.providers.mfa.domain import (
    MfaConfig,
    MfaFactor,
    MfaRecord,
    MfaRequest,
    MfaTargetProjectionConfig,
)
from identity_mapper.providers.mfa.mapper import (
    MfaCandidateMapper,
    MfaIdentityMapper,
    MfaMapper,
    MfaResolution,
)
from identity_mapper.providers.mfa.provider import InMemoryMfaStore

__all__ = [
    "InMemoryMfaStore",
    "MfaAuthenticationError",
    "MfaAuthenticator",
    "MfaCandidateMapper",
    "MfaConfig",
    "MfaCredentialVerifier",
    "MfaFactor",
    "MfaIdentityMapper",
    "MfaIdentityResolver",
    "MfaMapper",
    "MfaRecord",
    "MfaRequest",
    "MfaResolution",
    "MfaTargetIdentityMapper",
    "MfaTargetProjectionConfig",
]
