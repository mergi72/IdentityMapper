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
from identity_mapper.providers.oauth.domain import OAuthConfig
from identity_mapper.providers.oauth.mapper import (
    OAuthTokenCandidateMapper,
    OAuthTokenIdentityMapper,
    OAuthTokenResolution,
)
from identity_mapper.providers.oauth.provider import InMemoryOAuthTokenStore


class OAuthAuthenticationError(AuthenticationRejected):
    """Raised when OAuth authentication cannot produce an identity."""


class OAuthIdentityResolver(ResolveIdentity):
    """Resolves an OAuth subject to an identity candidate."""

    def __init__(
        self,
        store: InMemoryOAuthTokenStore,
        mapper: OAuthTokenCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or OAuthTokenCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        token = self._store.get_by_subject(identification.identifier)
        if token is None or not token.active:
            return None

        return self._mapper.to_domain(
            OAuthTokenResolution(
                token=token,
                identification=identification,
            )
        )


class OAuthCredentialVerifier(VerifyCredential):
    """Verifies an OAuth bearer token against a candidate."""

    def __init__(
        self,
        store: InMemoryOAuthTokenStore,
        config: OAuthConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or OAuthConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        token = self._store.get_by_token_id(candidate.implementation_id)
        if token is None or not token.active:
            return False

        return compare_digest(token.access_token, credential.value)


class OAuthAuthenticator(Authenticate):
    """Orchestrates OAuth identity resolution and token verification."""

    def __init__(
        self,
        store: InMemoryOAuthTokenStore,
        resolver: OAuthIdentityResolver | None = None,
        verifier: OAuthCredentialVerifier | None = None,
        identity_mapper: OAuthTokenIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or OAuthIdentityResolver(store)
        self._verifier = verifier or OAuthCredentialVerifier(store)
        self._identity_mapper = identity_mapper or OAuthTokenIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise OAuthAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise OAuthAuthenticationError("invalid credential")

        token = self._store.get_by_token_id(candidate.implementation_id)
        if token is None or not token.active:
            raise OAuthAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(token)
