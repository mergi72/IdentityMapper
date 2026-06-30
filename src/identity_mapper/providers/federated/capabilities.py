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
from identity_mapper.providers.federated.domain import (
    FederatedConfig,
    FederatedTargetProjectionConfig,
)
from identity_mapper.providers.federated.mapper import (
    FederatedCandidateMapper,
    FederatedIdentityMapper,
    FederatedResolution,
)
from identity_mapper.providers.federated.provider import InMemoryFederatedIdentityStore


class FederatedAuthenticationError(AuthenticationRejected):
    """Raised when federated authentication cannot produce an identity."""


class FederatedIdentityResolver(ResolveIdentity):
    """Resolves a federated subject to an identity candidate."""

    def __init__(
        self,
        store: InMemoryFederatedIdentityStore,
        mapper: FederatedCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or FederatedCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        if identification.realm is None:
            return None

        record = self._store.get_by_issuer_subject(
            identification.realm,
            identification.identifier,
        )
        if record is None or not record.active:
            return None

        return self._mapper.to_domain(
            FederatedResolution(
                record=record,
                identification=identification,
            )
        )


class FederatedCredentialVerifier(VerifyCredential):
    """Verifies a federation assertion against a candidate."""

    def __init__(
        self,
        store: InMemoryFederatedIdentityStore,
        config: FederatedConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or FederatedConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        record = self._store.get_by_trust_mapping_id(
            candidate.implementation_id
        )
        if record is None or not record.active:
            return False

        return compare_digest(record.assertion, credential.value)


class FederatedAuthenticator(Authenticate):
    """Orchestrates federated subject resolution and assertion verification."""

    def __init__(
        self,
        store: InMemoryFederatedIdentityStore,
        resolver: FederatedIdentityResolver | None = None,
        verifier: FederatedCredentialVerifier | None = None,
        identity_mapper: FederatedIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or FederatedIdentityResolver(store)
        self._verifier = verifier or FederatedCredentialVerifier(store)
        self._identity_mapper = (
            identity_mapper or FederatedIdentityMapper()
        )

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise FederatedAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise FederatedAuthenticationError("invalid credential")

        record = self._store.get_by_trust_mapping_id(
            candidate.implementation_id
        )
        if record is None or not record.active:
            raise FederatedAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(record)


class FederatedTargetIdentityMapper(MapIdentity):
    """Projects a verified Identity into a Federated target identity shape."""

    def __init__(
        self,
        config: FederatedTargetProjectionConfig | None = None,
    ) -> None:
        self._config = config or FederatedTargetProjectionConfig()

    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        if target.provider != self._config.provider:
            return None

        issuer = target.realm or self._config.default_issuer
        audience = target.purpose or self._config.default_audience
        external_subject_candidate = identity.email or identity.id
        return TargetIdentity(
            identifier=f"{target.provider}:{external_subject_candidate}",
            target=target,
            attributes={
                key: value
                for key, value in {
                    "external_subject_candidate": external_subject_candidate,
                    "issuer_hint": issuer,
                    "audience_hint": audience,
                    "claim_hints": dict(identity.claims),
                    "role_hints": tuple(identity.roles),
                    "mail_hint": identity.email,
                }.items()
                if value is not None
            },
        )
