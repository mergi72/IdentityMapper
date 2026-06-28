from dataclasses import dataclass

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.mapper import Mapper
from identity_mapper.providers.ldap.domain import LdapBindRequest, LdapConfig, LdapEntry


@dataclass(frozen=True, slots=True)
class LdapEntryResolution:
    """Implementation resolution result before credential verification."""

    entry: LdapEntry
    identification: Identification


LdapBindDomain = tuple[Identification, Credential]


class LdapBindMapper(Mapper[LdapBindRequest, LdapBindDomain]):
    """Maps an LDAP bind request to existing identity domain inputs."""

    def __init__(self, config: LdapConfig | None = None) -> None:
        self._config = config or LdapConfig()

    def to_domain(self, source: LdapBindRequest) -> LdapBindDomain:
        return (
            Identification(
                identifier=source.uid,
                realm=source.realm or self._config.realm,
            ),
            Credential(
                type=self._config.credential_type,
                value=source.password,
                metadata=dict(source.metadata),
            ),
        )


class LdapEntryCandidateMapper(Mapper[LdapEntryResolution, IdentityCandidate]):
    """Maps a resolved LDAP entry to an identity candidate."""

    def to_domain(self, source: LdapEntryResolution) -> IdentityCandidate:
        return IdentityCandidate(
            implementation_id=source.entry.dn,
            identification=source.identification,
            attributes=dict(source.entry.attributes),
        )


class LdapEntryIdentityMapper(Mapper[LdapEntry, Identity]):
    """Maps a verified LDAP entry to the identity invariant."""

    def to_domain(self, source: LdapEntry) -> Identity:
        return Identity(
            id=source.identity_id,
            display_name=source.cn,
            email=source.mail,
            roles=source.groups,
            claims=dict(source.claims),
            attributes=dict(source.attributes),
        )
