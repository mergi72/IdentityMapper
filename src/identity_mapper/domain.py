from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Identity:
    """Verified identity domain invariant."""

    id: str
    identifier: str
    realm: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Identification:
    """Claim that selects which identity should be verified."""

    identifier: str
    realm: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Credential:
    """Material used to verify an identification."""

    type: str
    value: str = field(repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)
