from __future__ import annotations

from dataclasses import dataclass

from identity_mapper.capability_protocol import AuthenticationRejected
from identity_mapper.capabilities import Authenticate, ResolveIdentity, VerifyCredential
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)


class UnknownProviderError(ValueError):
    """Raised when a requested provider is not registered."""


@dataclass(frozen=True, slots=True)
class ProviderAuthenticationResult:
    """Authentication result with the provider that accepted the request."""

    provider: str
    identity: Identity


@dataclass(frozen=True, slots=True)
class ProviderResolutionResult:
    """Resolution result with the provider that produced the candidate."""

    provider: str
    candidate: IdentityCandidate


class ProviderRegistry:
    """Registry of hosted provider capabilities."""

    def __init__(self) -> None:
        self._authenticators: dict[str, Authenticate] = {}
        self._resolvers: dict[str, ResolveIdentity] = {}
        self._verifiers: dict[str, VerifyCredential] = {}

    def register_authenticator(
        self,
        provider: str,
        authenticator: Authenticate,
    ) -> None:
        self._authenticators[provider] = authenticator

    def register_resolver(
        self,
        provider: str,
        resolver: ResolveIdentity,
    ) -> None:
        self._resolvers[provider] = resolver

    def register_verifier(
        self,
        provider: str,
        verifier: VerifyCredential,
    ) -> None:
        self._verifiers[provider] = verifier

    def providers(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                set(self._authenticators)
                | set(self._resolvers)
                | set(self._verifiers)
            )
        )

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

    def resolve_identity(
        self,
        provider: str | None,
        identification: Identification,
    ) -> ProviderResolutionResult | None:
        if provider is None:
            return self._resolve_with_first_matching_provider(identification)

        resolver = self._resolvers.get(provider)
        if resolver is None:
            raise UnknownProviderError(provider)

        candidate = resolver.resolve_identity(identification)
        if candidate is None:
            return None
        return ProviderResolutionResult(provider=provider, candidate=candidate)

    def _resolve_with_first_matching_provider(
        self,
        identification: Identification,
    ) -> ProviderResolutionResult | None:
        for provider in self.providers():
            resolver = self._resolvers.get(provider)
            if resolver is None:
                continue
            candidate = resolver.resolve_identity(identification)
            if candidate is not None:
                return ProviderResolutionResult(
                    provider=provider,
                    candidate=candidate,
                )
        return None

    def verify_credential(
        self,
        provider: str | None,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        if provider is None:
            return self._verify_with_first_matching_provider(candidate, credential)

        verifier = self._verifiers.get(provider)
        if verifier is None:
            raise UnknownProviderError(provider)

        return verifier.verify_credential(candidate, credential)

    def _verify_with_first_matching_provider(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> bool:
        for provider in self.providers():
            verifier = self._verifiers.get(provider)
            if verifier is not None and verifier.verify_credential(
                candidate,
                credential,
            ):
                return True
        return False
