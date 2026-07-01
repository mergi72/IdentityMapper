"""Windows / AD SID reference implementation."""

from identity_mapper.providers.windows.capabilities import (
    WindowsAuthenticationError,
    WindowsAdTargetIdentityMapper,
    WindowsAdTargetIdentityResolver,
    WindowsAuthenticator,
    WindowsCredentialVerifier,
    WindowsIdentityResolver,
)
from identity_mapper.providers.windows.domain import (
    WindowsAdTargetAccountRecord,
    WindowsAdTargetProjectionConfig,
    WindowsConfig,
    WindowsIdentityRecord,
    WindowsIdentityRequest,
)
from identity_mapper.providers.windows.mapper import (
    WindowsCandidateMapper,
    WindowsIdentityMapper,
    WindowsMapper,
    WindowsResolution,
)
from identity_mapper.providers.windows.provider import (
    InMemoryWindowsAdTargetDirectory,
    InMemoryWindowsIdentityStore,
)

__all__ = [
    "InMemoryWindowsAdTargetDirectory",
    "InMemoryWindowsIdentityStore",
    "WindowsAuthenticationError",
    "WindowsAdTargetAccountRecord",
    "WindowsAdTargetIdentityMapper",
    "WindowsAdTargetIdentityResolver",
    "WindowsAdTargetProjectionConfig",
    "WindowsAuthenticator",
    "WindowsCandidateMapper",
    "WindowsConfig",
    "WindowsCredentialVerifier",
    "WindowsIdentityMapper",
    "WindowsIdentityRecord",
    "WindowsIdentityRequest",
    "WindowsIdentityResolver",
    "WindowsMapper",
    "WindowsResolution",
]
