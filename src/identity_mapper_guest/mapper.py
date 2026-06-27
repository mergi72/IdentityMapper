from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper_guest.domain import (
    GuestConfig,
    GuestRequest,
    GuestSessionRecord,
)


@dataclass(frozen=True, slots=True)
class GuestResolution:
    """Implementation resolution result before guest session verification."""

    session: GuestSessionRecord
    identification: Identification


GuestDomain = tuple[Identification, Credential]


class GuestMapper(Mapper[GuestRequest, GuestDomain]):
    """Maps a guest request to existing identity domain inputs."""

    def __init__(self, config: GuestConfig | None = None) -> None:
        self._config = config or GuestConfig()

    def to_domain(self, source: GuestRequest) -> GuestDomain:
        return (
            Identification(
                identifier=source.session_id,
                realm=source.realm or self._config.realm,
                attributes={"kind": "guest"},
            ),
            Credential(
                type=self._config.credential_type,
                value=source.session_token,
                metadata=dict(source.metadata),
            ),
        )


class GuestCandidateMapper(Mapper[GuestResolution, IdentityCandidate]):
    """Maps a resolved guest session to an identity candidate."""

    def to_domain(self, source: GuestResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.session.session_id,
            identification=source.identification,
            attributes=dict(source.session.attributes),
        )


class GuestIdentityMapper(Mapper[GuestSessionRecord, Identity]):
    """Maps a verified guest session to the identity invariant."""

    def to_domain(self, source: GuestSessionRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
