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
from identity_mapper.providers.guest.domain import GuestConfig
from identity_mapper.providers.guest.mapper import (
    GuestCandidateMapper,
    GuestIdentityMapper,
    GuestResolution,
)
from identity_mapper.providers.guest.provider import InMemoryGuestSessionStore


class GuestAuthenticationError(AuthenticationRejected):
    """Raised when guest authentication cannot produce an identity."""


class GuestIdentityResolver(ResolveIdentity):
    """Resolves a guest session id to an identity candidate."""

    def __init__(
        self,
        store: InMemoryGuestSessionStore,
        mapper: GuestCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or GuestCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        session = self._store.get_by_session_id(identification.identifier)
        if session is None or not session.active:
            return None

        return self._mapper.to_domain(
            GuestResolution(
                session=session,
                identification=identification,
            )
        )


class GuestCredentialVerifier(VerifyCredential):
    """Verifies a guest session token against a candidate."""

    def __init__(
        self,
        store: InMemoryGuestSessionStore,
        config: GuestConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or GuestConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        session = self._store.get_by_session_id(candidate.implementation_id)
        if session is None or not session.active:
            return False

        return compare_digest(session.session_token, credential.value)


class GuestAuthenticator(Authenticate):
    """Orchestrates guest session resolution and token verification."""

    def __init__(
        self,
        store: InMemoryGuestSessionStore,
        resolver: GuestIdentityResolver | None = None,
        verifier: GuestCredentialVerifier | None = None,
        identity_mapper: GuestIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or GuestIdentityResolver(store)
        self._verifier = verifier or GuestCredentialVerifier(store)
        self._identity_mapper = identity_mapper or GuestIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise GuestAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise GuestAuthenticationError("invalid credential")

        session = self._store.get_by_session_id(candidate.implementation_id)
        if session is None or not session.active:
            raise GuestAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(session)
