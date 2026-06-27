from dataclasses import dataclass, field
from typing import Any

from identity_mapper.domain import Credential, Identification
from identity_mapper.mapper import Mapper


@dataclass(frozen=True, slots=True)
class BasicAuthenticationRequest:
    """Implementation model for a basic identifier and secret pair."""

    identifier: str
    secret: str = field(repr=False)
    realm: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


BasicAuthenticationDomain = tuple[Identification, Credential]


class BasicAuthenticationMapper(
    Mapper[BasicAuthenticationRequest, BasicAuthenticationDomain]
):
    """Maps a basic authentication request to identity domain inputs."""

    def to_domain(
        self,
        source: BasicAuthenticationRequest,
    ) -> BasicAuthenticationDomain:
        return (
            Identification(
                identifier=source.identifier,
                realm=source.realm,
            ),
            Credential(
                type="PASSWORD",
                value=source.secret,
                metadata=dict(source.metadata),
            ),
        )
