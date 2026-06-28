from hmac import compare_digest

from identity_mapper.capability_protocol import AuthenticationRejected

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
from identity_mapper.providers.basic.domain import BasicAuthConfig
from identity_mapper.providers.basic.mapper import (
    BasicUserCandidateMapper,
    BasicUserIdentityMapper,
    BasicUserResolution,
)
from identity_mapper.providers.basic.provider import InMemoryBasicUserStore


class BasicAuthenticationError(AuthenticationRejected):
    """Raised when basic authentication cannot produce an identity."""


class BasicIdentityResolver(ResolveIdentity):
    """Resolves a basic username to an identity candidate."""

    def __init__(
        self,
        store: InMemoryBasicUserStore,
        mapper: BasicUserCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or BasicUserCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        user = self._store.get_by_username(identification.identifier)
        if user is None:
            return None

        return self._mapper.to_domain(
            BasicUserResolution(
                user=user,
                identification=identification,
            )
        )


class BasicCredentialVerifier(VerifyCredential):
    """Verifies a basic password credential against a candidate."""

    def __init__(
        self,
        store: InMemoryBasicUserStore,
        config: BasicAuthConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or BasicAuthConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        user = self._store.get_by_implementation_id(candidate.implementation_id)
        if user is None:
            return False

        return compare_digest(user.password, credential.value)


class BasicAuthenticator(Authenticate):
    """Orchestrates basic identity resolution and credential verification."""

    def __init__(
        self,
        store: InMemoryBasicUserStore,
        resolver: BasicIdentityResolver | None = None,
        verifier: BasicCredentialVerifier | None = None,
        identity_mapper: BasicUserIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or BasicIdentityResolver(store)
        self._verifier = verifier or BasicCredentialVerifier(store)
        self._identity_mapper = identity_mapper or BasicUserIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise BasicAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise BasicAuthenticationError("invalid credential")

        user = self._store.get_by_implementation_id(candidate.implementation_id)
        if user is None:
            raise BasicAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(user)
