"""IdentityMapper package."""

from identity_mapper.capabilities import (
    Authenticate,
    ResolveIdentity,
    VerifyCredential,
)
from identity_mapper.capability_protocol import (
    AuthenticationRejected,
    AuthenticateRequest,
    AuthenticateResponse,
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
    "Mapper",
    "ReductionMatrix",
    "ReductionSections",
    "ResolveIdentity",
    "ResolveIdentityRequest",
    "ResolveIdentityResponse",
    "VerifyCredential",
    "VerifyCredentialRequest",
    "VerifyCredentialResponse",
]
