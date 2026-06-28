from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ReductionSections:
    """Section-based reduction matrix shape."""

    identification: dict[str, Any]
    credential: dict[str, Any]
    candidate: dict[str, Any]
    identity: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ReductionMatrix:
    """Provider-owned reduction matrix targeting a domain invariant."""

    template: str
    provider: str
    invariant: str
    sections: ReductionSections

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ReductionMatrix":
        sections = ReductionSections(
            identification=value["identification"],
            credential=value["credential"],
            candidate=value["candidate"],
            identity=value["identity"],
        )
        return cls(
            template=value["template"],
            provider=value["provider"],
            invariant=value["invariant"],
            sections=sections,
        )
