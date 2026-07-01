from __future__ import annotations

from dataclasses import dataclass

from identity_mapper.capability_protocol import AuthenticationRejected
from identity_mapper.capabilities import (
    Authenticate,
    MapIdentity,
    ResolveIdentity,
    ResolveTargetIdentity,
    VerifyCredential,
)
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
    IdentityTarget,
    TargetIdentity,
    TargetIdentityResolution,
)


class UnknownProviderError(ValueError):
    """Raised when a requested provider is not registered."""


class UnknownTargetMapperError(ValueError):
    """Raised when a requested target mapper is not registered."""


class UnknownTargetResolverError(ValueError):
    """Raised when a requested target resolver is not registered."""


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


@dataclass(frozen=True, slots=True)
class ProviderVerificationResult:
    """Verification result with the provider that handled the request."""

    provider: str
    verified: bool


@dataclass(frozen=True, slots=True)
class IdentityMappingResult:
    """Identity mapping result with the source provider and target mapper."""

    source_provider: str
    target_mapper: str
    identity: Identity
    target_identity: TargetIdentity | None


@dataclass(frozen=True, slots=True)
class TargetIdentityResolutionResult:
    """Target identity resolution result with the target resolver."""

    target_resolver: str
    resolution: TargetIdentityResolution


class ProviderRegistry:
    """Registry of hosted provider capabilities."""

    def __init__(self) -> None:
        self._authenticators: dict[str, Authenticate] = {}
        self._resolvers: dict[str, ResolveIdentity] = {}
        self._verifiers: dict[str, VerifyCredential] = {}
        self._identity_mappers: dict[str, MapIdentity] = {}
        self._target_resolvers: dict[str, ResolveTargetIdentity] = {}

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

    def register_identity_mapper(
        self,
        target_mapper: str,
        mapper: MapIdentity,
    ) -> None:
        self._identity_mappers[target_mapper] = mapper

    def register_target_resolver(
        self,
        target_resolver: str,
        resolver: ResolveTargetIdentity,
    ) -> None:
        self._target_resolvers[target_resolver] = resolver

    def providers(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                set(self._authenticators)
                | set(self._resolvers)
                | set(self._verifiers)
                | set(self._identity_mappers)
                | set(self._target_resolvers)
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
        for provider in sorted(self._authenticators):
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
    ) -> ProviderVerificationResult:
        if provider is None:
            return self._verify_with_first_matching_provider(candidate, credential)

        verifier = self._verifiers.get(provider)
        if verifier is None:
            raise UnknownProviderError(provider)

        return ProviderVerificationResult(
            provider=provider,
            verified=verifier.verify_credential(candidate, credential),
        )

    def _verify_with_first_matching_provider(
        self,
        candidate: IdentityCandidate,
        credential: Credential,
    ) -> ProviderVerificationResult:
        for provider in self.providers():
            verifier = self._verifiers.get(provider)
            if verifier is not None and verifier.verify_credential(
                candidate,
                credential,
            ):
                return ProviderVerificationResult(provider=provider, verified=True)
        return ProviderVerificationResult(provider="auto", verified=False)

    def map_identity(
        self,
        source_provider: str | None,
        identification: Identification,
        credential: Credential,
        target: IdentityTarget,
    ) -> IdentityMappingResult:
        target_mapper = target.provider
        mapper = self._identity_mappers.get(target_mapper)
        if mapper is None:
            raise UnknownTargetMapperError(target_mapper)

        authentication = self.authenticate(
            source_provider,
            identification,
            credential,
        )

        return IdentityMappingResult(
            source_provider=authentication.provider,
            target_mapper=target_mapper,
            identity=authentication.identity,
            target_identity=mapper.map_identity(authentication.identity, target),
        )

    def resolve_target_identity(
        self,
        target_identity: TargetIdentity,
    ) -> TargetIdentityResolutionResult:
        target_resolver = target_identity.target.provider
        resolver = self._target_resolvers.get(target_resolver)
        if resolver is None:
            raise UnknownTargetResolverError(target_resolver)

        return TargetIdentityResolutionResult(
            target_resolver=target_resolver,
            resolution=resolver.resolve_target_identity(target_identity),
        )
