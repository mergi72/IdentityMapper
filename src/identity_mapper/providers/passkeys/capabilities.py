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
from identity_mapper.providers.passkeys.domain import PasskeyConfig
from identity_mapper.providers.passkeys.mapper import (
    PasskeyCandidateMapper,
    PasskeyIdentityMapper,
    PasskeyResolution,
)
from identity_mapper.providers.passkeys.provider import InMemoryPasskeyStore


class PasskeyAuthenticationError(AuthenticationRejected):
    """Raised when passkey authentication cannot produce an identity."""


class PasskeyIdentityResolver(ResolveIdentity):
    """Resolves a passkey id to an identity candidate."""

    def __init__(
        self,
        store: InMemoryPasskeyStore,
        mapper: PasskeyCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or PasskeyCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        passkey = self._store.get_by_passkey_id(identification.identifier)
        if passkey is None or not passkey.active:
            return None

        return self._mapper.to_domain(
            PasskeyResolution(
                passkey=passkey,
                identification=identification,
            )
        )


class PasskeyCredentialVerifier(VerifyCredential):
    """Verifies a passkey assertion against a candidate."""

    def __init__(
        self,
        store: InMemoryPasskeyStore,
        config: PasskeyConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or PasskeyConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        passkey = self._store.get_by_passkey_id(candidate.implementation_id)
        if passkey is None or not passkey.active:
            return False

        return compare_digest(passkey.assertion, credential.value)


class PasskeyAuthenticator(Authenticate):
    """Orchestrates passkey resolution and assertion verification."""

    def __init__(
        self,
        store: InMemoryPasskeyStore,
        resolver: PasskeyIdentityResolver | None = None,
        verifier: PasskeyCredentialVerifier | None = None,
        identity_mapper: PasskeyIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or PasskeyIdentityResolver(store)
        self._verifier = verifier or PasskeyCredentialVerifier(store)
        self._identity_mapper = identity_mapper or PasskeyIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise PasskeyAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise PasskeyAuthenticationError("invalid credential")

        passkey = self._store.get_by_passkey_id(candidate.implementation_id)
        if passkey is None or not passkey.active:
            raise PasskeyAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(passkey)
