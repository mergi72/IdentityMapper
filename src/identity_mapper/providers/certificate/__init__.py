"""Client Certificate / mTLS reference implementation."""

from identity_mapper.providers.certificate.capabilities import (
    ClientCertificateAuthenticationError,
    ClientCertificateAuthenticator,
    ClientCertificateCredentialVerifier,
    ClientCertificateIdentityResolver,
)
from identity_mapper.providers.certificate.domain import (
    ClientCertificateConfig,
    ClientCertificateRecord,
    ClientCertificateRequest,
)
from identity_mapper.providers.certificate.mapper import (
    ClientCertificateCandidateMapper,
    ClientCertificateIdentityMapper,
    ClientCertificateMapper,
    ClientCertificateResolution,
)
from identity_mapper.providers.certificate.provider import InMemoryClientCertificateStore

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
