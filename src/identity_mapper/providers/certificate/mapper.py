from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.providers.certificate.domain import (
    ClientCertificateConfig,
    ClientCertificateRecord,
    ClientCertificateRequest,
)


@dataclass(frozen=True, slots=True)
class ClientCertificateResolution:
    """Implementation resolution result before certificate proof verification."""

    certificate: ClientCertificateRecord
    identification: Identification


ClientCertificateDomain = tuple[Identification, Credential]


class ClientCertificateMapper(
    Mapper[ClientCertificateRequest, ClientCertificateDomain]
):
    """Maps a client certificate request to existing identity domain inputs."""

    def __init__(self, config: ClientCertificateConfig | None = None) -> None:
        self._config = config or ClientCertificateConfig()

    def to_domain(
        self,
        source: ClientCertificateRequest,
    ) -> ClientCertificateDomain:
        return (
            Identification(
                identifier=source.fingerprint,
                realm=self._config.realm,
                attributes={
                    key: value
                    for key, value in {
                        "subject": source.subject,
                        "issuer": source.issuer,
                        "serial_number": source.serial_number,
                    }.items()
                    if value is not None
                },
            ),
            Credential(
                type=self._config.credential_type,
                value=source.proof,
                metadata=dict(source.metadata),
            ),
        )


class ClientCertificateCandidateMapper(
    Mapper[ClientCertificateResolution, IdentityCandidate]
):
    """Maps a resolved certificate record to an identity candidate."""

    def to_domain(
        self,
        source: ClientCertificateResolution,
    ) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.certificate.fingerprint,
            identification=source.identification,
            attributes=dict(source.certificate.attributes),
        )


class ClientCertificateIdentityMapper(
    Mapper[ClientCertificateRecord, Identity]
):
    """Maps a verified certificate record to the identity invariant."""

    def to_domain(self, source: ClientCertificateRecord) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.display_name,
            email=source.email,
            roles=source.roles,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
