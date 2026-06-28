from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.providers.webauthn.domain import (
    WebAuthnConfig,
    WebAuthnCredentialRecord,
    WebAuthnRequest,
)


@dataclass(frozen=True, slots=True)
class WebAuthnResolution:
    """Implementation resolution result before assertion verification."""

    credential: WebAuthnCredentialRecord
    identification: Identification


WebAuthnDomain = tuple[Identification, Credential]


class WebAuthnMapper(Mapper[WebAuthnRequest, WebAuthnDomain]):
    """Maps a WebAuthn request to existing identity domain inputs."""

    def __init__(self, config: WebAuthnConfig | None = None) -> None:
        self._config = config or WebAuthnConfig()

    def to_domain(self, source: WebAuthnRequest) -> WebAuthnDomain:
        return (
            Identification(
                identifier=source.credential_id,
                realm=source.relying_party_id or self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "user_handle": source.user_handle,
                        "challenge": source.challenge,
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


class WebAuthnCandidateMapper(
    Mapper[WebAuthnResolution, IdentityCandidate]
):
    """Maps a resolved WebAuthn credential to an identity candidate."""

    def to_domain(self, source: WebAuthnResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.credential.credential_id,
            identification=source.identification,
            attributes=dict(source.credential.attributes),
        )


class WebAuthnIdentityMapper(Mapper[WebAuthnCredentialRecord, Identity]):
    """Maps a verified WebAuthn credential to the identity invariant."""

    def to_domain(self, source: WebAuthnCredentialRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
