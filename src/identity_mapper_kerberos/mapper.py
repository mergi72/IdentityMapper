from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper_kerberos.domain import (
    KerberosConfig,
    KerberosPrincipalRecord,
    KerberosRequest,
)


@dataclass(frozen=True, slots=True)
class KerberosResolution:
    """Implementation resolution result before ticket verification."""

    principal: KerberosPrincipalRecord
    identification: Identification


KerberosDomain = tuple[Identification, Credential]


class KerberosMapper(Mapper[KerberosRequest, KerberosDomain]):
    """Maps a Kerberos request to existing identity domain inputs."""

    def __init__(self, config: KerberosConfig | None = None) -> None:
        self._config = config or KerberosConfig()

    def to_domain(self, source: KerberosRequest) -> KerberosDomain:
        return (
            Identification(
                identifier=source.principal,
                realm=source.realm or self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "service": source.service,
                    }.items()
                    if value is not None
                },
            ),
            Credential(
                type=self._config.credential_type,
                value=source.ticket,
                metadata=dict(source.metadata),
            ),
        )


class KerberosCandidateMapper(Mapper[KerberosResolution, IdentityCandidate]):
    """Maps a resolved Kerberos principal to an identity candidate."""

    def to_domain(self, source: KerberosResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.principal.principal,
            identification=source.identification,
            attributes=dict(source.principal.attributes),
        )


class KerberosIdentityMapper(Mapper[KerberosPrincipalRecord, Identity]):
    """Maps a verified Kerberos principal to the identity invariant."""

    def to_domain(self, source: KerberosPrincipalRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
