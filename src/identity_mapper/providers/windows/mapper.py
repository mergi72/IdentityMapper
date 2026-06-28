from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.providers.windows.domain import (
    WindowsConfig,
    WindowsIdentityRecord,
    WindowsIdentityRequest,
)


@dataclass(frozen=True, slots=True)
class WindowsResolution:
    """Implementation resolution result before logon proof verification."""

    identity: WindowsIdentityRecord
    identification: Identification


WindowsDomain = tuple[Identification, Credential]


class WindowsMapper(Mapper[WindowsIdentityRequest, WindowsDomain]):
    """Maps a Windows identity request to existing identity domain inputs."""

    def __init__(self, config: WindowsConfig | None = None) -> None:
        self._config = config or WindowsConfig()

    def to_domain(self, source: WindowsIdentityRequest) -> WindowsDomain:
        return (
            Identification(
                identifier=source.sid,
                realm=source.domain or self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "upn": source.upn,
                    }.items()
                    if value is not None
                },
            ),
            Credential(
                type=self._config.credential_type,
                value=source.logon_proof,
                metadata=dict(source.metadata),
            ),
        )


class WindowsCandidateMapper(Mapper[WindowsResolution, IdentityCandidate]):
    """Maps a resolved Windows identity to an identity candidate."""

    def to_domain(self, source: WindowsResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.identity.sid,
            identification=source.identification,
            attributes=dict(source.identity.attributes),
        )


class WindowsIdentityMapper(Mapper[WindowsIdentityRecord, Identity]):
    """Maps a verified Windows identity to the identity invariant."""

    def to_domain(self, source: WindowsIdentityRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
