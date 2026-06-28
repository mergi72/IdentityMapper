from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class MatrixRow:
    """One reduction matrix row."""

    section: str
    domain: str
    source: str | None = None
    literal: str | None = None

    def __post_init__(self) -> None:
        if (self.source is None) == (self.literal is None):
            raise ValueError("MatrixRow requires exactly one of source or literal.")


@dataclass(frozen=True, slots=True)
class ReductionMatrix:
    """Provider-owned reduction matrix targeting a domain invariant."""

    template: str
    provider: str
    invariant: str
    rows: tuple[MatrixRow, ...]

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ReductionMatrix":
        rows = tuple(MatrixRow(**row) for row in value["rows"])
        return cls(
            template=value["template"],
            provider=value["provider"],
            invariant=value["invariant"],
            rows=rows,
        )
