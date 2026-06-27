"""Client Certificate / mTLS reference implementation."""

from identity_mapper_certificate.capabilities import (
    ClientCertificateAuthenticationError,
    ClientCertificateAuthenticator,
    ClientCertificateCredentialVerifier,
    ClientCertificateIdentityResolver,
)
from identity_mapper_certificate.domain import (
    ClientCertificateConfig,
    ClientCertificateRecord,
    ClientCertificateRequest,
)
from identity_mapper_certificate.mapper import (
    ClientCertificateCandidateMapper,
    ClientCertificateIdentityMapper,
    ClientCertificateMapper,
    ClientCertificateResolution,
)
from identity_mapper_certificate.provider import InMemoryClientCertificateStore

__all__ = [
    "ClientCertificateAuthenticationError",
    "ClientCertificateAuthenticator",
    "ClientCertificateCandidateMapper",
    "ClientCertificateConfig",
    "ClientCertificateCredentialVerifier",
    "ClientCertificateIdentityMapper",
    "ClientCertificateIdentityResolver",
    "ClientCertificateMapper",
    "ClientCertificateRecord",
    "ClientCertificateRequest",
    "ClientCertificateResolution",
    "InMemoryClientCertificateStore",
]
