"""Local OS user target identity reference implementation."""

from identity_mapper.providers.local_user.capabilities import (
    LocalUserTargetIdentityMapper,
    LocalUserTargetIdentityResolver,
)
from identity_mapper.providers.local_user.domain import (
    LocalUserAccountRecord,
    LocalUserTargetProjectionConfig,
)
from identity_mapper.providers.local_user.provider import (
    InMemoryLocalUserAccountDirectory,
    LocalUserAccountDirectory,
)

__all__ = [
    "InMemoryLocalUserAccountDirectory",
    "LocalUserAccountDirectory",
    "LocalUserAccountRecord",
    "LocalUserTargetIdentityMapper",
    "LocalUserTargetIdentityResolver",
    "LocalUserTargetProjectionConfig",
]
