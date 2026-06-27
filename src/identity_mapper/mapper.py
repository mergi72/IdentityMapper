from abc import ABC, abstractmethod
from typing import Generic, TypeVar


ImplementationModel = TypeVar("ImplementationModel")
DomainModel = TypeVar("DomainModel")


class Mapper(ABC, Generic[ImplementationModel, DomainModel]):
    """Maps an implementation model to a domain invariant."""

    @abstractmethod
    def to_domain(self, source: ImplementationModel) -> DomainModel:
        """Translate an implementation-specific model into a domain model."""
