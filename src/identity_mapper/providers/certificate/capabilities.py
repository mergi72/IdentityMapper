from hmac import compare_digest

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
from identity_mapper.providers.certificate.domain import ClientCertificateConfig
from identity_mapper.providers.certificate.mapper import (
    ClientCertificateCandidateMapper,
    ClientCertificateIdentityMapper,
    ClientCertificateResolution,
)
from identity_mapper.providers.certificate.provider import InMemoryClientCertificateStore


class ClientCertificateAuthenticationError(ValueError):
    """Raised when certificate authentication cannot produce an identity."""


class ClientCertificateIdentityResolver(ResolveIdentity):
    """Resolves a certificate fingerprint to an identity candidate."""

    def __init__(
        self,
        store: InMemoryClientCertificateStore,
        mapper: ClientCertificateCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or ClientCertificateCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        certificate = self._store.get_by_fingerprint(
            identification.identifier
        )
        if certificate is None or not certificate.active:
            return None

        return self._mapper.to_domain(
            ClientCertificateResolution(
                certificate=certificate,
                identification=identification,
            )
        )


class ClientCertificateCredentialVerifier(VerifyCredential):
    """Verifies a certificate proof against a candidate."""

    def __init__(
        self,
        store: InMemoryClientCertificateStore,
        config: ClientCertificateConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or ClientCertificateConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        certificate = self._store.get_by_fingerprint(
            candidate.implementation_id
        )
        if certificate is None or not certificate.active:
            return False

        return compare_digest(certificate.proof, credential.value)


class ClientCertificateAuthenticator(Authenticate):
    """Orchestrates certificate resolution and proof verification."""

    def __init__(
        self,
        store: InMemoryClientCertificateStore,
        resolver: ClientCertificateIdentityResolver | None = None,
        verifier: ClientCertificateCredentialVerifier | None = None,
        identity_mapper: ClientCertificateIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or ClientCertificateIdentityResolver(store)
        self._verifier = verifier or ClientCertificateCredentialVerifier(
            store
        )
        self._identity_mapper = (
            identity_mapper or ClientCertificateIdentityMapper()
        )

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise ClientCertificateAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise ClientCertificateAuthenticationError("invalid credential")

        certificate = self._store.get_by_fingerprint(
            candidate.implementation_id
        )
        if certificate is None or not certificate.active:
            raise ClientCertificateAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(certificate)
