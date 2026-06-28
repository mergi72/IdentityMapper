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
from identity_mapper.providers.webauthn.domain import WebAuthnConfig
from identity_mapper.providers.webauthn.mapper import (
    WebAuthnCandidateMapper,
    WebAuthnIdentityMapper,
    WebAuthnResolution,
)
from identity_mapper.providers.webauthn.provider import InMemoryWebAuthnCredentialStore


class WebAuthnAuthenticationError(AuthenticationRejected):
    """Raised when WebAuthn authentication cannot produce an identity."""


class WebAuthnIdentityResolver(ResolveIdentity):
    """Resolves a WebAuthn credential id to an identity candidate."""

    def __init__(
        self,
        store: InMemoryWebAuthnCredentialStore,
        mapper: WebAuthnCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or WebAuthnCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        credential = self._store.get_by_credential_id(
            identification.identifier
        )
        if credential is None or not credential.active:
            return None

        return self._mapper.to_domain(
            WebAuthnResolution(
                credential=credential,
                identification=identification,
            )
        )


class WebAuthnCredentialVerifier(VerifyCredential):
    """Verifies a WebAuthn assertion against a candidate."""

    def __init__(
        self,
        store: InMemoryWebAuthnCredentialStore,
        config: WebAuthnConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or WebAuthnConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        webauthn_credential = self._store.get_by_credential_id(
            candidate.implementation_id
        )
        if webauthn_credential is None or not webauthn_credential.active:
            return False

        return compare_digest(webauthn_credential.assertion, credential.value)


class WebAuthnAuthenticator(Authenticate):
    """Orchestrates WebAuthn credential resolution and assertion verification."""

    def __init__(
        self,
        store: InMemoryWebAuthnCredentialStore,
        resolver: WebAuthnIdentityResolver | None = None,
        verifier: WebAuthnCredentialVerifier | None = None,
        identity_mapper: WebAuthnIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or WebAuthnIdentityResolver(store)
        self._verifier = verifier or WebAuthnCredentialVerifier(store)
        self._identity_mapper = identity_mapper or WebAuthnIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise WebAuthnAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise WebAuthnAuthenticationError("invalid credential")

        webauthn_credential = self._store.get_by_credential_id(
            candidate.implementation_id
        )
        if webauthn_credential is None or not webauthn_credential.active:
            raise WebAuthnAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(webauthn_credential)
