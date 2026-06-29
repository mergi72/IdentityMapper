"""IdentityMapper package."""

from identity_mapper.capabilities import (
    Authenticate,
    MapIdentity,
    ResolveIdentity,
    VerifyCredential,
)
from identity_mapper.capability_protocol import (
    AuthenticationRejected,
    AuthenticateRequest,
    AuthenticateResponse,
    MapIdentityRequest,
    MapIdentityResponse,
    ResolveIdentityRequest,
    ResolveIdentityResponse,
    VerifyCredentialRequest,
    VerifyCredentialResponse,
)
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
)
from identity_mapper.mapper import Mapper
from identity_mapper.matrix import ReductionMatrix, ReductionSections

__all__ = [
    "Authenticate",
    "AuthenticationRejected",
    "AuthenticateRequest",
    "AuthenticateResponse",
    "Credential",
    "Identification",
    "Identity",
    "IdentityCandidate",
    "IdentityTarget",
    "MapIdentity",
    "MapIdentityRequest",
    "MapIdentityResponse",
    "Mapper",
    "ReductionMatrix",
    "ReductionSections",
    "ResolveIdentity",
    "ResolveIdentityRequest",
    "ResolveIdentityResponse",
    "TargetIdentity",
    "VerifyCredential",
    "VerifyCredentialRequest",
    "VerifyCredentialResponse",
]
