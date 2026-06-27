from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper_oauth.domain import (
    OAuthConfig,
    OAuthTokenRecord,
    OAuthTokenRequest,
)


@dataclass(frozen=True, slots=True)
class OAuthTokenResolution:
    """Implementation resolution result before token verification."""

    token: OAuthTokenRecord
    identification: Identification


OAuthTokenDomain = tuple[Identification, Credential]


class OAuthTokenMapper(Mapper[OAuthTokenRequest, OAuthTokenDomain]):
    """Maps an OAuth token request to existing identity domain inputs."""

    def __init__(self, config: OAuthConfig | None = None) -> None:
        self._config = config or OAuthConfig()

    def to_domain(self, source: OAuthTokenRequest) -> OAuthTokenDomain:
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
                value=source.access_token,
                metadata=dict(source.metadata),
            ),
        )


class OAuthTokenCandidateMapper(
    Mapper[OAuthTokenResolution, IdentityCandidate]
):
    """Maps a resolved OAuth token record to an identity candidate."""

    def to_domain(self, source: OAuthTokenResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.token.token_id,
            identification=source.identification,
            attributes=dict(source.token.attributes),
        )


class OAuthTokenIdentityMapper(Mapper[OAuthTokenRecord, Identity]):
    """Maps a verified OAuth token record to the identity invariant."""

    def to_domain(self, source: OAuthTokenRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.scopes,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
