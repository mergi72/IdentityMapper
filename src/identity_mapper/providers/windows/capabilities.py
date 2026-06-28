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
from identity_mapper.providers.windows.domain import WindowsConfig
from identity_mapper.providers.windows.mapper import (
    WindowsCandidateMapper,
    WindowsIdentityMapper,
    WindowsResolution,
)
from identity_mapper.providers.windows.provider import InMemoryWindowsIdentityStore


class WindowsAuthenticationError(AuthenticationRejected):
    """Raised when Windows authentication cannot produce an identity."""


class WindowsIdentityResolver(ResolveIdentity):
    """Resolves a Windows SID to an identity candidate."""

    def __init__(
        self,
        store: InMemoryWindowsIdentityStore,
        mapper: WindowsCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or WindowsCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        identity = self._store.get_by_sid(identification.identifier)
        if identity is None or not identity.active:
            return None

        return self._mapper.to_domain(
            WindowsResolution(
                identity=identity,
                identification=identification,
            )
        )


class WindowsCredentialVerifier(VerifyCredential):
    """Verifies a Windows logon proof against a candidate."""

    def __init__(
        self,
        store: InMemoryWindowsIdentityStore,
        config: WindowsConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or WindowsConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        identity = self._store.get_by_sid(candidate.implementation_id)
        if identity is None or not identity.active:
            return False

        return compare_digest(identity.logon_proof, credential.value)


class WindowsAuthenticator(Authenticate):
    """Orchestrates Windows SID resolution and logon proof verification."""

    def __init__(
        self,
        store: InMemoryWindowsIdentityStore,
        resolver: WindowsIdentityResolver | None = None,
        verifier: WindowsCredentialVerifier | None = None,
        identity_mapper: WindowsIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or WindowsIdentityResolver(store)
        self._verifier = verifier or WindowsCredentialVerifier(store)
        self._identity_mapper = identity_mapper or WindowsIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise WindowsAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise WindowsAuthenticationError("invalid credential")

        identity = self._store.get_by_sid(candidate.implementation_id)
        if identity is None or not identity.active:
            raise WindowsAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(identity)
