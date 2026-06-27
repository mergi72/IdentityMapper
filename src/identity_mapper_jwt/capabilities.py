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
from identity_mapper_jwt.domain import JwtConfig
from identity_mapper_jwt.mapper import (
    JwtCandidateMapper,
    JwtIdentityMapper,
    JwtResolution,
)
from identity_mapper_jwt.provider import InMemoryJwtStore


class JwtAuthenticationError(ValueError):
    """Raised when JWT / Bearer Token authentication cannot produce identity."""


class JwtIdentityResolver(ResolveIdentity):
    """Resolves a JWT subject to an identity candidate."""

    def __init__(
        self,
        store: InMemoryJwtStore,
        mapper: JwtCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or JwtCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        token = self._store.get_by_subject(identification.identifier)
        if token is None or not token.active:
            return None

        return self._mapper.to_domain(
            JwtResolution(
                token=token,
                identification=identification,
            )
        )


class JwtCredentialVerifier(VerifyCredential):
    """Verifies a bearer token against a candidate."""

    def __init__(
        self,
        store: InMemoryJwtStore,
        config: JwtConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or JwtConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        token = self._store.get_by_jwt_id(candidate.implementation_id)
        if token is None or not token.active:
            return False

        return compare_digest(token.bearer_token, credential.value)


class JwtAuthenticator(Authenticate):
    """Orchestrates JWT identity resolution and bearer token verification."""

    def __init__(
        self,
        store: InMemoryJwtStore,
        resolver: JwtIdentityResolver | None = None,
        verifier: JwtCredentialVerifier | None = None,
        identity_mapper: JwtIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or JwtIdentityResolver(store)
        self._verifier = verifier or JwtCredentialVerifier(store)
        self._identity_mapper = identity_mapper or JwtIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise JwtAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise JwtAuthenticationError("invalid credential")

        token = self._store.get_by_jwt_id(candidate.implementation_id)
        if token is None or not token.active:
            raise JwtAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(token)
