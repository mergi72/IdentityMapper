from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class HealthResponse:
    """Response produced by the Host Service health surface."""

    status: str


@dataclass(frozen=True, slots=True)
class ProvidersResponse:
    """Response produced by the Host Service provider listing surface."""

    providers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AuditResponse:
    """Response produced by the Host Service audit surface."""

    entries: tuple[dict[str, Any], ...]
