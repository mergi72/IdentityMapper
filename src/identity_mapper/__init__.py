"""IdentityMapper package."""

from identity_mapper.capabilities import (
    Authenticate,
    ResolveIdentity,
    VerifyCredential,
)
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.matrix import ReductionMatrix, ReductionSections
from identity_mapper.requests import (
    AuthenticateRequest,
    ResolveIdentityRequest,
    VerifyCredentialRequest,
)
from identity_mapper.responses import (
    AuthenticateResponse,
    ResolveIdentityResponse,
    VerifyCredentialResponse,
)

__all__ = [
    "Authenticate",
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
