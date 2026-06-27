from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper_saml.domain import (
    SamlAssertionRecord,
    SamlConfig,
    SamlRequest,
)


@dataclass(frozen=True, slots=True)
class SamlResolution:
    """Implementation resolution result before assertion verification."""

    assertion: SamlAssertionRecord
    identification: Identification


SamlDomain = tuple[Identification, Credential]


class SamlMapper(Mapper[SamlRequest, SamlDomain]):
    """Maps a SAML request to existing identity domain inputs."""

    def __init__(self, config: SamlConfig | None = None) -> None:
        self._config = config or SamlConfig()

    def to_domain(self, source: SamlRequest) -> SamlDomain:
        return (
            Identification(
                identifier=source.name_id,
                realm=source.issuer or self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "audience": source.audience,
                        "session_index": source.session_index,
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


class SamlCandidateMapper(Mapper[SamlResolution, IdentityCandidate]):
    """Maps a resolved SAML assertion to an identity candidate."""

    def to_domain(self, source: SamlResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.assertion.assertion_id,
            identification=source.identification,
            attributes=dict(source.assertion.attributes),
        )


class SamlIdentityMapper(Mapper[SamlAssertionRecord, Identity]):
    """Maps a verified SAML assertion to the identity invariant."""

    def to_domain(self, source: SamlAssertionRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
