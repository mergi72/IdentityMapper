from abc import ABC, abstractmethod

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
    TargetIdentityResolution,
)


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
    def resolve_identity(
        self,
        identification: Identification,
    ) -> IdentityCandidate | None:
        """Return the candidate for an identification, if one exists."""


class VerifyCredential(ABC):
    """Verifies that a credential belongs to an identity candidate."""

    @abstractmethod
    def verify_credential(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        """Return whether the credential verifies the candidate."""


class MapIdentity(ABC):
    """Maps a canonical identity into a target identity world."""

    @abstractmethod
    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        """Return a target identity projection, if one can be produced."""


class ResolveTargetIdentity(ABC):
    """Looks up a projected target identity in its target identity world."""

    @abstractmethod
    def resolve_target_identity(
        self,
        target_identity: TargetIdentity,
    ) -> TargetIdentityResolution:
        """Return the read-only target lookup result."""
