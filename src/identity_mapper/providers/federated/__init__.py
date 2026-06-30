"""Federated identity reference implementation."""

from identity_mapper.providers.federated.capabilities import (
    FederatedAuthenticationError,
    FederatedAuthenticator,
    FederatedCredentialVerifier,
    FederatedIdentityResolver,
    FederatedTargetIdentityMapper,
)
from identity_mapper.providers.federated.domain import (
    FederatedConfig,
    FederatedIdentityRecord,
    FederatedRequest,
    FederatedTargetProjectionConfig,
)
from identity_mapper.providers.federated.mapper import (
    FederatedCandidateMapper,
    FederatedIdentityMapper,
    FederatedMapper,
    FederatedResolution,
)
from identity_mapper.providers.federated.provider import InMemoryFederatedIdentityStore

__all__ = [
    "FederatedAuthenticationError",
    "FederatedAuthenticator",
    "FederatedCandidateMapper",
    "FederatedConfig",
    "FederatedCredentialVerifier",
    "FederatedIdentityMapper",
    "FederatedIdentityRecord",
    "FederatedIdentityResolver",
    "FederatedMapper",
    "FederatedRequest",
    "FederatedResolution",
    "FederatedTargetIdentityMapper",
    "FederatedTargetProjectionConfig",
    "InMemoryFederatedIdentityStore",
]
