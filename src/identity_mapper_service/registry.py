from __future__ import annotations

from dataclasses import dataclass

from identity_mapper.capability_protocol import AuthenticationRejected
from identity_mapper.capabilities import Authenticate
from identity_mapper.domain import Credential, Identification, Identity


class UnknownProviderError(ValueError):
    """Raised when a requested provider is not registered."""


@dataclass(frozen=True, slots=True)
class ProviderAuthenticationResult:
    """Authentication result with the provider that accepted the request."""

    provider: str
    identity: Identity


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
        provider: str | None,
        identification: Identification,
        credential: Credential,
    ) -> ProviderAuthenticationResult:
        if provider is None:
            return self._authenticate_with_first_matching_provider(
                identification,
                credential,
            )

        authenticator = self._authenticators.get(provider)
        if authenticator is None:
            raise UnknownProviderError(provider)

        return ProviderAuthenticationResult(
            provider=provider,
            identity=authenticator.authenticate(identification, credential),
        )

    def _authenticate_with_first_matching_provider(
        self,
        identification: Identification,
        credential: Credential,
    ) -> ProviderAuthenticationResult:
        for provider in self.providers():
            authenticator = self._authenticators[provider]
            try:
                identity = authenticator.authenticate(identification, credential)
            except AuthenticationRejected:
                continue
            return ProviderAuthenticationResult(provider=provider, identity=identity)

        raise AuthenticationRejected("no provider accepted the request")
