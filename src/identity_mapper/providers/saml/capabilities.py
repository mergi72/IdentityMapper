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
from identity_mapper.providers.saml.domain import SamlConfig, SamlTargetProjectionConfig
from identity_mapper.providers.saml.mapper import (
    SamlCandidateMapper,
    SamlIdentityMapper,
    SamlResolution,
)
from identity_mapper.providers.saml.provider import InMemorySamlAssertionStore


class SamlAuthenticationError(AuthenticationRejected):
    """Raised when SAML authentication cannot produce an identity."""


class SamlIdentityResolver(ResolveIdentity):
    """Resolves a SAML NameID to an identity candidate."""

    def __init__(
        self,
        store: InMemorySamlAssertionStore,
        mapper: SamlCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or SamlCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        assertion = self._store.get_by_name_id(identification.identifier)
        if assertion is None or not assertion.active:
            return None

        return self._mapper.to_domain(
            SamlResolution(
                assertion=assertion,
                identification=identification,
            )
        )


class SamlCredentialVerifier(VerifyCredential):
    """Verifies a SAML assertion against a candidate."""

    def __init__(
        self,
        store: InMemorySamlAssertionStore,
        config: SamlConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or SamlConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        assertion = self._store.get_by_assertion_id(
            candidate.implementation_id
        )
        if assertion is None or not assertion.active:
            return False

        return compare_digest(assertion.assertion, credential.value)


class SamlAuthenticator(Authenticate):
    """Orchestrates SAML NameID resolution and assertion verification."""

    def __init__(
        self,
        store: InMemorySamlAssertionStore,
        resolver: SamlIdentityResolver | None = None,
        verifier: SamlCredentialVerifier | None = None,
        identity_mapper: SamlIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or SamlIdentityResolver(store)
        self._verifier = verifier or SamlCredentialVerifier(store)
        self._identity_mapper = identity_mapper or SamlIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise SamlAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise SamlAuthenticationError("invalid credential")

        assertion = self._store.get_by_assertion_id(
            candidate.implementation_id
        )
        if assertion is None or not assertion.active:
            raise SamlAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(assertion)


class SamlTargetIdentityMapper(MapIdentity):
    """Projects a verified Identity into a SAML target identity shape."""

    def __init__(
        self,
        config: SamlTargetProjectionConfig | None = None,
    ) -> None:
        self._config = config or SamlTargetProjectionConfig()

    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        if target.provider != self._config.provider:
            return None

        issuer = target.realm or self._config.default_issuer
        audience = target.purpose or self._config.default_audience
        name_id_candidate = identity.email or identity.id
        return TargetIdentity(
            identifier=f"{target.provider}:{name_id_candidate}",
            target=target,
            attributes={
                key: value
                for key, value in {
                    "name_id_candidate": name_id_candidate,
                    "issuer_hint": issuer,
                    "audience_hint": audience,
                    "attribute_hints": dict(identity.attributes),
                    "claim_hints": dict(identity.claims),
                    "role_hints": tuple(identity.roles),
                }.items()
                if value is not None
            },
        )
