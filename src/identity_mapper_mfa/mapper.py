from dataclasses import dataclass
import json

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper_mfa.domain import (
    MfaConfig,
    MfaFactor,
    MfaRecord,
    MfaRequest,
)


@dataclass(frozen=True, slots=True)
class MfaResolution:
    """Implementation resolution result before factor verification."""

    record: MfaRecord
    identification: Identification


MfaDomain = tuple[Identification, Credential]


def encode_factors(factors: tuple[MfaFactor, ...]) -> str:
    """Encode MFA factors into a stable credential payload."""

    payload = [
        {
            "metadata": factor.metadata,
            "type": factor.type,
            "value": factor.value,
        }
        for factor in sorted(factors, key=lambda factor: factor.type)
    ]
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


class MfaMapper(Mapper[MfaRequest, MfaDomain]):
    """Maps an MFA request to existing identity domain inputs."""

    def __init__(self, config: MfaConfig | None = None) -> None:
        self._config = config or MfaConfig()

    def to_domain(self, source: MfaRequest) -> MfaDomain:
        return (
            Identification(
                identifier=source.identifier,
                realm=source.realm or self._config.realm,
            ),
            Credential(
                type=self._config.credential_type,
                value=encode_factors(source.factors),
                metadata={
                    **dict(source.metadata),
                    "factor_count": len(source.factors),
                },
            ),
        )


class MfaCandidateMapper(Mapper[MfaResolution, IdentityCandidate]):
    """Maps a resolved MFA record to an identity candidate."""

    def to_domain(self, source: MfaResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.record.implementation_id,
            identification=source.identification,
            attributes=dict(source.record.attributes),
        )


class MfaIdentityMapper(Mapper[MfaRecord, Identity]):
    """Maps a verified MFA record to the identity invariant."""

    def to_domain(self, source: MfaRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
