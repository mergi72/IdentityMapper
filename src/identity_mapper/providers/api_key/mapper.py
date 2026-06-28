from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.providers.api_key.domain import (
    ApiKeyConfig,
    ApiKeyRecord,
    ApiKeyRequest,
)


@dataclass(frozen=True, slots=True)
class ApiKeyResolution:
    """Implementation resolution result before API key verification."""

    key: ApiKeyRecord
    identification: Identification


ApiKeyDomain = tuple[Identification, Credential]


class ApiKeyMapper(Mapper[ApiKeyRequest, ApiKeyDomain]):
    """Maps an API key request to existing identity domain inputs."""

    def __init__(self, config: ApiKeyConfig | None = None) -> None:
        self._config = config or ApiKeyConfig()

    def to_domain(self, source: ApiKeyRequest) -> ApiKeyDomain:
        return (
            Identification(
                identifier=source.key_id,
                realm=self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "client_id": source.client_id,
                    }.items()
                    if value is not None
                },
            ),
            Credential(
                type=self._config.credential_type,
                value=source.api_key,
                metadata=dict(source.metadata),
            ),
        )


class ApiKeyCandidateMapper(Mapper[ApiKeyResolution, IdentityCandidate]):
    """Maps a resolved API key record to an identity candidate."""

    def to_domain(self, source: ApiKeyResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.key.key_id,
            identification=source.identification,
            attributes=dict(source.key.attributes),
        )


class ApiKeyIdentityMapper(Mapper[ApiKeyRecord, Identity]):
    """Maps a verified API key record to the identity invariant."""

    def to_domain(self, source: ApiKeyRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
