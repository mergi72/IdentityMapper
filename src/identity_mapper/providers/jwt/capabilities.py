from hmac import compare_digest

from identity_mapper.capability_protocol import AuthenticationRejected

from identity_mapper.capabilities import (
    Authenticate,
    MapIdentity,
    ResolveIdentity,
    VerifyCredential,
)
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
)
from identity_mapper.providers.jwt.domain import JwtConfig, JwtTargetProjectionConfig
from identity_mapper.providers.jwt.mapper import (
    JwtCandidateMapper,
    JwtIdentityMapper,
    JwtResolution,
)
from identity_mapper.providers.jwt.provider import InMemoryJwtStore


class JwtAuthenticationError(AuthenticationRejected):
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


class JwtTargetIdentityMapper(MapIdentity):
    """Projects a verified Identity into a JWT target identity shape."""

    def __init__(
        self,
        config: JwtTargetProjectionConfig | None = None,
    ) -> None:
        self._config = config or JwtTargetProjectionConfig()

    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        if target.provider != self._config.provider:
            return None

        issuer = target.realm or self._config.default_issuer
        audience = target.purpose or self._config.default_audience
        subject_candidate = identity.id
        return TargetIdentity(
            identifier=f"{target.provider}:{subject_candidate}",
            target=target,
            attributes={
                key: value
                for key, value in {
                    "subject_candidate": subject_candidate,
                    "issuer_hint": issuer,
                    "audience_hint": audience,
                    "email_hint": identity.email,
                    "claim_hints": dict(identity.claims),
                    "role_hints": tuple(identity.roles),
                }.items()
                if value is not None
            },
        )
