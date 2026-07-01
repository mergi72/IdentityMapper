from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class LocalUserTargetProjectionConfig:
    """Configuration for projecting an Identity into a local user target world."""

    provider: str = "local_user"
    default_realm: str | None = None


@dataclass(frozen=True, slots=True)
class LocalUserAccountRecord:
    """Read-only local user account record used by target lookup."""

    username: str
    uid: int | None = None
    gid: int | None = None
    home: str | None = None
    shell: str | None = None
    display_name: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
