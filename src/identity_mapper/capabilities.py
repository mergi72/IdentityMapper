from abc import ABC, abstractmethod

from identity_mapper.domain import Credential, Identification, Identity


class Authenticate(ABC):
    """Orchestrates identity resolution and credential verification."""

    @abstractmethod
    def authenticate(
        self,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        """Authenticate an identification and return the verified identity."""


class ResolveIdentity(ABC):
    """Finds an identity candidate by identification."""

    @abstractmethod
    def resolve_identity(self, identification: Identification) -> Identity | None:
        """Return the identity for an identification, if one exists."""


class VerifyCredential(ABC):
    """Verifies that a credential belongs to an identity."""

    @abstractmethod
    def verify_credential(
        self,
        identity: Identity,
        credential: Credential,
    ) -> bool:
        """Return whether the credential verifies the identity."""
