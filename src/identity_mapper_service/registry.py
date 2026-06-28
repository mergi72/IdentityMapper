from __future__ import annotations

from identity_mapper.capabilities import Authenticate
from identity_mapper.domain import Credential, Identification, Identity


class UnknownProviderError(ValueError):
    """Raised when a requested provider is not registered."""


class ProviderRegistry:
    """Registry of hosted provider capabilities."""

    def __init__(self) -> None:
        self._authenticators: dict[str, Authenticate] = {}

    def register_authenticator(
        self,
        provider: str,
        authenticator: Authenticate,
    ) -> None:
        self._authenticators[provider] = authenticator

    def providers(self) -> tuple[str, ...]:
        return tuple(sorted(self._authenticators))

    def authenticate(
        self,
        provider: str,
        identification: Identification,
        credential: Credential,
    ) -> Identity:
        authenticator = self._authenticators.get(provider)
        if authenticator is None:
            raise UnknownProviderError(provider)

        return authenticator.authenticate(identification, credential)
