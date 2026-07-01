from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class WindowsConfig:
    """Configuration for the Windows / AD SID implementation."""

    realm: str | None = None
    credential_type: str = "WINDOWS_LOGON_PROOF"


@dataclass(frozen=True, slots=True)
class WindowsIdentityRequest:
    """Implementation model for a Windows identity authentication request."""

    sid: str
    logon_proof: str = field(repr=False)
    upn: str | None = None
    domain: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WindowsIdentityRecord:
    """Implementation model for a Windows identity record."""

    sid: str
    logon_proof: str = field(repr=False)
    identity_id: str
    active: bool = True
    upn: str | None = None
    domain: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WindowsAdTargetProjectionConfig:
    """Configuration for projecting an Identity into a Windows / AD target world."""

    provider: str = "ad"
    default_realm: str | None = None


@dataclass(frozen=True, slots=True)
class WindowsAdTargetAccountRecord:
    """Read-only Windows / AD account record used by target lookup."""

    sid: str
    upn: str
    sam_account_name: str
    distinguished_name: str | None = None
    active: bool = True
    attributes: dict[str, Any] = field(default_factory=dict)
