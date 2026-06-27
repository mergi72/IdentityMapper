from hmac import compare_digest
import json
from typing import Any

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
from identity_mapper_mfa.domain import MfaConfig
from identity_mapper_mfa.mapper import (
    MfaCandidateMapper,
    MfaIdentityMapper,
    MfaResolution,
)
from identity_mapper_mfa.provider import InMemoryMfaStore


class MfaAuthenticationError(ValueError):
    """Raised when MFA authentication cannot produce an identity."""


class MfaIdentityResolver(ResolveIdentity):
    """Resolves an MFA identifier to an identity candidate."""

    def __init__(
        self,
        store: InMemoryMfaStore,
        mapper: MfaCandidateMapper | None = None,
    ) -> None:
        self._store = store
        self._mapper = mapper or MfaCandidateMapper()

    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        record = self._store.get_by_identifier(identification.identifier)
        if record is None or not record.active:
            return None

        return self._mapper.to_domain(
            MfaResolution(
                record=record,
                identification=identification,
            )
        )


class MfaCredentialVerifier(VerifyCredential):
    """Verifies MFA factors against a candidate."""

    def __init__(
        self,
        store: InMemoryMfaStore,
        config: MfaConfig | None = None,
    ) -> None:
        self._store = store
        self._config = config or MfaConfig()

    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if credential.type != self._config.credential_type:
            return False

        record = self._store.get_by_implementation_id(
            candidate.implementation_id
        )
        if record is None or not record.active:
            return False

        provided_factors = self._decode_factor_values(credential.value)
        if set(provided_factors) != set(record.required_factors):
            return False

        return all(
            compare_digest(record.required_factors[factor_type], value)
            for factor_type, value in provided_factors.items()
        )

    def _decode_factor_values(self, value: str) -> dict[str, str]:
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return {}

        if not isinstance(decoded, list):
            return {}

        factors: dict[str, str] = {}
        for item in decoded:
            if not self._is_factor_payload(item):
                return {}
            factors[item["type"]] = item["value"]
        return factors

    def _is_factor_payload(self, item: Any) -> bool:
        return (
            isinstance(item, dict)
            and isinstance(item.get("type"), str)
            and isinstance(item.get("value"), str)
        )


class MfaAuthenticator(Authenticate):
    """Orchestrates MFA identity resolution and factor verification."""

    def __init__(
        self,
        store: InMemoryMfaStore,
        resolver: MfaIdentityResolver | None = None,
        verifier: MfaCredentialVerifier | None = None,
        identity_mapper: MfaIdentityMapper | None = None,
    ) -> None:
        self._store = store
        self._resolver = resolver or MfaIdentityResolver(store)
        self._verifier = verifier or MfaCredentialVerifier(store)
        self._identity_mapper = identity_mapper or MfaIdentityMapper()

    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        candidate = self._resolver.resolve_identity(identification)
        if candidate is None:
            raise MfaAuthenticationError("unknown identity")

        if not self._verifier.verify_credential(candidate, credential):
            raise MfaAuthenticationError("invalid credential")

        record = self._store.get_by_implementation_id(
            candidate.implementation_id
        )
        if record is None or not record.active:
            raise MfaAuthenticationError("unknown identity")

        return self._identity_mapper.to_domain(record)
