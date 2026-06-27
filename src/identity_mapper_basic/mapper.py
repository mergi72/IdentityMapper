from dataclasses import dataclass, field
from typing import Any

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper_basic.domain import BasicAuthConfig, BasicUserRecord


@dataclass(frozen=True, slots=True)
class BasicAuthenticationRequest:
    """Implementation model for a basic user/password request."""

    username: str
    password: str = field(repr=False)
    realm: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BasicUserResolution:
    """Implementation resolution result before credential verification."""

    user: BasicUserRecord
    identification: Identification


BasicAuthenticationDomain = tuple[Identification, Credential]


class BasicAuthenticationMapper(
    Mapper[BasicAuthenticationRequest, BasicAuthenticationDomain]
):
    """Maps a basic request to existing identity domain inputs."""

    def __init__(self, config: BasicAuthConfig | None = None) -> None:
        self._config = config or BasicAuthConfig()

    def to_domain(
        self,
        source: BasicAuthenticationRequest,
    ) -> BasicAuthenticationDomain:
        return (
            Identification(
                identifier=source.username,
                realm=source.realm or self._config.realm,
            ),
            Credential(
                type=self._config.credential_type,
                value=source.password,
                metadata=dict(source.metadata),
            ),
        )


class BasicUserCandidateMapper(
    Mapper[BasicUserResolution, IdentityCandidate]
):
    """Maps a resolved basic user record to an identity candidate."""

    def to_domain(self, source: BasicUserResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.user.implementation_id,
            identification=source.identification,
            attributes=dict(source.user.attributes),
        )


class BasicUserIdentityMapper(Mapper[BasicUserRecord, Identity]):
    """Maps a verified basic user record to the identity invariant."""

    def to_domain(self, source: BasicUserRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
