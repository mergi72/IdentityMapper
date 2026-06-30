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
from identity_mapper.providers.api_key.domain import (
    ApiKeyConfig,
    ApiKeyTargetProjectionConfig,
)
from identity_mapper.providers.api_key.mapper import (
    ApiKeyCandidateMapper,
    ApiKeyIdentityMapper,
    ApiKeyResolution,
)
from identity_mapper.providers.api_key.provider import InMemoryApiKeyStore


class ApiKeyAuthenticationError(AuthenticationRejected):
    """Raised when API key authentication cannot produce an identity."""


class ApiKeyIdentityResolver(ResolveIdentity):
    """Resolves an API key identifier to an identity candidate."""

    def __init__(
        self,
        store: InMemoryApiKeyStore,
        mapper: ApiKeyCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or ApiKeyCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        key = self._store.get_by_key_id(identification.identifier)
        if key is None or not key.active:
            return None

        return self._mapper.to_domain(
            ApiKeyResolution(
                key=key,
                identification=identification,
            )
        )


class ApiKeyCredentialVerifier(VerifyCredential):
    """Verifies an API key credential against a candidate."""

    def __init__(
        self,
        store: InMemoryApiKeyStore,
        config: ApiKeyConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or ApiKeyConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        key = self._store.get_by_key_id(candidate.implementation_id)
        if key is None or not key.active:
            return False

        return compare_digest(key.api_key, credential.value)


class ApiKeyAuthenticator(Authenticate):
    """Orchestrates API key identity resolution and credential verification."""

    def __init__(
        self,
        store: InMemoryApiKeyStore,
        resolver: ApiKeyIdentityResolver | None = None,
        verifier: ApiKeyCredentialVerifier | None = None,
        identity_mapper: ApiKeyIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or ApiKeyIdentityResolver(store)
        self._verifier = verifier or ApiKeyCredentialVerifier(store)
        self._identity_mapper = identity_mapper or ApiKeyIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise ApiKeyAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise ApiKeyAuthenticationError("invalid credential")

        key = self._store.get_by_key_id(candidate.implementation_id)
        if key is None or not key.active:
            raise ApiKeyAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(key)


class ApiKeyTargetIdentityMapper(MapIdentity):
    """Projects a verified Identity into an API Key target identity shape."""

    def __init__(
        self,
        config: ApiKeyTargetProjectionConfig | None = None,
    ) -> None:
        self._config = config or ApiKeyTargetProjectionConfig()

    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        if target.provider != self._config.provider:
            return None

        client_id = target.realm or self._config.default_client_id
        key_id_candidate = f"{identity.id}:api-key"
        return TargetIdentity(
            identifier=f"{target.provider}:{key_id_candidate}",
            target=target,
            attributes={
                key: value
                for key, value in {
                    "key_id_candidate": key_id_candidate,
                    "client_id_hint": client_id,
                    "display_name_hint": identity.display_name,
                    "mail_hint": identity.email,
                    "role_hints": tuple(identity.roles),
                    "claim_hints": dict(identity.claims),
                }.items()
                if value is not None
            },
        )
