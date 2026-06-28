from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.providers.passkeys.domain import (
    PasskeyConfig,
    PasskeyRecord,
    PasskeyRequest,
)


@dataclass(frozen=True, slots=True)
class PasskeyResolution:
    """Implementation resolution result before assertion verification."""

    passkey: PasskeyRecord
    identification: Identification


PasskeyDomain = tuple[Identification, Credential]


class PasskeyMapper(Mapper[PasskeyRequest, PasskeyDomain]):
    """Maps a passkey request to existing identity domain inputs."""

    def __init__(self, config: PasskeyConfig | None = None) -> None:
        self._config = config or PasskeyConfig()

    def to_domain(self, source: PasskeyRequest) -> PasskeyDomain:
        return (
            Identification(
                identifier=source.passkey_id,
                realm=source.relying_party_id or self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "user_handle": source.user_handle,
                        "device_name": source.device_name,
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


class PasskeyCandidateMapper(Mapper[PasskeyResolution, IdentityCandidate]):
    """Maps a resolved passkey record to an identity candidate."""

    def to_domain(self, source: PasskeyResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.passkey.passkey_id,
            identification=source.identification,
            attributes=dict(source.passkey.attributes),
        )


class PasskeyIdentityMapper(Mapper[PasskeyRecord, Identity]):
    """Maps a verified passkey record to the identity invariant."""

    def to_domain(self, source: PasskeyRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
