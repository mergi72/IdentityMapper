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
from identity_mapper.matrix import MatrixRow, ReductionMatrix

__all__ = [
    "Authenticate",
    "Credential",
    "Identification",
    "Identity",
    "IdentityCandidate",
    "MatrixRow",
    "Mapper",
    "ReductionMatrix",
    "ResolveIdentity",
    "VerifyCredential",
]
