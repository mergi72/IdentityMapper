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
from identity_mapper_ldap.domain import LdapConfig
from identity_mapper_ldap.mapper import (
    LdapEntryCandidateMapper,
    LdapEntryIdentityMapper,
    LdapEntryResolution,
)
from identity_mapper_ldap.provider import InMemoryLdapDirectory


class LdapAuthenticationError(ValueError):
    """Raised when LDAP authentication cannot produce an identity."""


class LdapIdentityResolver(ResolveIdentity):
    """Resolves an LDAP uid to an identity candidate."""

    def __init__(
        self,
        directory: InMemoryLdapDirectory,
        mapper: LdapEntryCandidateMapper | None = None,
    ) -> None:
        self._directory = directory
        self._mapper = mapper or LdapEntryCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        entry = self._directory.get_by_uid(identification.identifier)
        if entry is None:
            return None

        return self._mapper.to_domain(
            LdapEntryResolution(
                entry=entry,
                identification=identification,
            )
        )


class LdapCredentialVerifier(VerifyCredential):
    """Verifies an LDAP password credential against a candidate."""

    def __init__(
        self,
        directory: InMemoryLdapDirectory,
        config: LdapConfig | None = None,
    ) -> None:
        self._directory = directory
        self._config = config or LdapConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        entry = self._directory.get_by_dn(candidate.implementation_id)
        if entry is None:
            return False

        return compare_digest(entry.user_password, credential.value)


class LdapAuthenticator(Authenticate):
    """Orchestrates LDAP identity resolution and credential verification."""

    def __init__(
        self,
        directory: InMemoryLdapDirectory,
        resolver: LdapIdentityResolver | None = None,
        verifier: LdapCredentialVerifier | None = None,
        identity_mapper: LdapEntryIdentityMapper | None = None,
    ) -> None:
        self._directory = directory
        self._resolver = resolver or LdapIdentityResolver(directory)
        self._verifier = verifier or LdapCredentialVerifier(directory)
        self._identity_mapper = identity_mapper or LdapEntryIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise LdapAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise LdapAuthenticationError("invalid credential")

        entry = self._directory.get_by_dn(candidate.implementation_id)
        if entry is None:
            raise LdapAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(entry)
