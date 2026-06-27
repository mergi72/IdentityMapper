"""Kerberos reference implementation."""

from identity_mapper_kerberos.capabilities import (
    KerberosAuthenticationError,
    KerberosAuthenticator,
    KerberosCredentialVerifier,
    KerberosIdentityResolver,
)
from identity_mapper_kerberos.domain import (
    KerberosConfig,
    KerberosPrincipalRecord,
    KerberosRequest,
)
from identity_mapper_kerberos.mapper import (
    KerberosCandidateMapper,
    KerberosIdentityMapper,
    KerberosMapper,
    KerberosResolution,
)
from identity_mapper_kerberos.provider import InMemoryKerberosPrincipalStore

__all__ = [
    "InMemoryKerberosPrincipalStore",
    "KerberosAuthenticationError",
    "KerberosAuthenticator",
    "KerberosCandidateMapper",
    "KerberosConfig",
    "KerberosCredentialVerifier",
    "KerberosIdentityMapper",
    "KerberosIdentityResolver",
    "KerberosMapper",
    "KerberosPrincipalRecord",
    "KerberosRequest",
    "KerberosResolution",
]
