"""Federated identity reference implementation."""

from identity_mapper_federated.capabilities import (
    FederatedAuthenticationError,
    FederatedAuthenticator,
    FederatedCredentialVerifier,
    FederatedIdentityResolver,
)
from identity_mapper_federated.domain import (
    FederatedConfig,
    FederatedIdentityRecord,
    FederatedRequest,
)
from identity_mapper_federated.mapper import (
    FederatedCandidateMapper,
    FederatedIdentityMapper,
    FederatedMapper,
    FederatedResolution,
)
from identity_mapper_federated.provider import InMemoryFederatedIdentityStore

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
    "InMemoryFederatedIdentityStore",
]
