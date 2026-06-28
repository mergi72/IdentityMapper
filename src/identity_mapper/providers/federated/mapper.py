from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.providers.federated.domain import (
    FederatedConfig,
    FederatedIdentityRecord,
    FederatedRequest,
)


@dataclass(frozen=True, slots=True)
class FederatedResolution:
    """Implementation resolution result before assertion verification."""

    record: FederatedIdentityRecord
    identification: Identification


FederatedDomain = tuple[Identification, Credential]


class FederatedMapper(Mapper[FederatedRequest, FederatedDomain]):
    """Maps a federated request to existing identity domain inputs."""

    def __init__(self, config: FederatedConfig | None = None) -> None:
        self._config = config or FederatedConfig()

    def to_domain(self, source: FederatedRequest) -> FederatedDomain:
        return (
            Identification(
                identifier=source.external_subject,
                realm=source.issuer or self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "audience": source.audience,
                        "issuer": source.issuer,
                    }.items()
                    if value is not None
                },
            ),
            Credential(
                type=self._config.credential_type,
                value=source.assertion,
                metadata=dict(source.metadata),
            ),
        )


class FederatedCandidateMapper(
    Mapper[FederatedResolution, IdentityCandidate]
):
    """Maps a resolved trust mapping to an identity candidate."""

    def to_domain(self, source: FederatedResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.record.trust_mapping_id,
            identification=source.identification,
            attributes=dict(source.record.attributes),
        )


class FederatedIdentityMapper(
    Mapper[FederatedIdentityRecord, Identity]
):
    """Maps a verified trust mapping to the identity invariant."""

    def to_domain(self, source: FederatedIdentityRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
