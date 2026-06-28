from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class LdapConfig:
    """Configuration for the LDAP implementation."""

    realm: str | None = None
    credential_type: str = "PASSWORD"


@dataclass(frozen=True, slots=True)
class LdapBindRequest:
    """Implementation model for an LDAP bind request."""

    uid: str
    password: str = field(repr=False)
    realm: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class LdapEntry:
    """Implementation model for an LDAP directory entry."""

    dn: str
    uid: str
    user_password: str = field(repr=False)
    identity_id: str
    active: bool = True
    cn: str | None = None
    mail: str | None = None
    groups: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)
