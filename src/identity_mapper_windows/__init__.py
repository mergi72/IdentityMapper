"""Windows / AD SID reference implementation."""

from identity_mapper_windows.capabilities import (
    WindowsAuthenticationError,
    WindowsAuthenticator,
    WindowsCredentialVerifier,
    WindowsIdentityResolver,
)
from identity_mapper_windows.domain import (
    WindowsConfig,
    WindowsIdentityRecord,
    WindowsIdentityRequest,
)
from identity_mapper_windows.mapper import (
    WindowsCandidateMapper,
    WindowsIdentityMapper,
    WindowsMapper,
    WindowsResolution,
)
from identity_mapper_windows.provider import InMemoryWindowsIdentityStore

__all__ = [
    "InMemoryWindowsIdentityStore",
    "WindowsAuthenticationError",
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
