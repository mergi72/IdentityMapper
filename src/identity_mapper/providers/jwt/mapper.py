from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.providers.jwt.domain import (
    JwtConfig,
    JwtRecord,
    JwtRequest,
)


@dataclass(frozen=True, slots=True)
class JwtResolution:
    """Implementation resolution result before token verification."""

    token: JwtRecord
    identification: Identification


JwtDomain = tuple[Identification, Credential]


class JwtMapper(Mapper[JwtRequest, JwtDomain]):
    """Maps a JWT / Bearer Token request to existing identity domain inputs."""

    def __init__(self, config: JwtConfig | None = None) -> None:
        self._config = config or JwtConfig()

    def to_domain(self, source: JwtRequest) -> JwtDomain:
        return (
            Identification(
                identifier=source.subject,
                realm=source.issuer or self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "audience": source.audience,
                    }.items()
                    if value is not None
                },
            ),
            Credential(
                type=self._config.credential_type,
                value=source.bearer_token,
                metadata=dict(source.metadata),
            ),
        )


class JwtCandidateMapper(Mapper[JwtResolution, IdentityCandidate]):
    """Maps a resolved JWT / Bearer Token record to an identity candidate."""

    def to_domain(self, source: JwtResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.token.jwt_id,
            identification=source.identification,
            attributes=dict(source.token.attributes),
        )


class JwtIdentityMapper(Mapper[JwtRecord, Identity]):
    """Maps a verified JWT / Bearer Token record to the identity invariant."""

    def to_domain(self, source: JwtRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
