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
from identity_mapper.providers.kerberos.domain import KerberosConfig
from identity_mapper.providers.kerberos.mapper import (
    KerberosCandidateMapper,
    KerberosIdentityMapper,
    KerberosResolution,
)
from identity_mapper.providers.kerberos.provider import InMemoryKerberosPrincipalStore


class KerberosAuthenticationError(ValueError):
    """Raised when Kerberos authentication cannot produce an identity."""


class KerberosIdentityResolver(ResolveIdentity):
    """Resolves a Kerberos principal to an identity candidate."""

    def __init__(
        self,
        store: InMemoryKerberosPrincipalStore,
        mapper: KerberosCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or KerberosCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        principal = self._store.get_by_principal(identification.identifier)
        if principal is None or not principal.active:
            return None

        return self._mapper.to_domain(
            KerberosResolution(
                principal=principal,
                identification=identification,
            )
        )


class KerberosCredentialVerifier(VerifyCredential):
    """Verifies a Kerberos ticket against a candidate."""

    def __init__(
        self,
        store: InMemoryKerberosPrincipalStore,
        config: KerberosConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or KerberosConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        principal = self._store.get_by_principal(candidate.implementation_id)
        if principal is None or not principal.active:
            return False

        return compare_digest(principal.ticket, credential.value)


class KerberosAuthenticator(Authenticate):
    """Orchestrates Kerberos principal resolution and ticket verification."""

    def __init__(
        self,
        store: InMemoryKerberosPrincipalStore,
        resolver: KerberosIdentityResolver | None = None,
        verifier: KerberosCredentialVerifier | None = None,
        identity_mapper: KerberosIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or KerberosIdentityResolver(store)
        self._verifier = verifier or KerberosCredentialVerifier(store)
        self._identity_mapper = identity_mapper or KerberosIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise KerberosAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise KerberosAuthenticationError("invalid credential")

        principal = self._store.get_by_principal(
            candidate.implementation_id
        )
        if principal is None or not principal.active:
            raise KerberosAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(principal)
