from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from identity_mapper.capability_protocol import (
    AuthenticationRejected,
    AuthenticateRequest,
    AuthenticateResponse,
    MapIdentityRequest,
    MapIdentityResponse,
    ResolveIdentityRequest,
    ResolveIdentityResponse,
    VerifyCredentialRequest,
    VerifyCredentialResponse,
)
from identity_mapper_service.registry import ProviderRegistry, UnknownProviderError
from identity_mapper_service.request_log import CapabilityInvocationLog
from identity_mapper_service.responses import (
    AuditResponse,
    HealthResponse,
    ProvidersResponse,
)


class IdentityMapperHostService:
    """Host facade for IdentityMapper capabilities."""

    def __init__(
        self,
        registry: ProviderRegistry,
        request_log: CapabilityInvocationLog | None = None,
    ) -> None:
        self._registry = registry
        self._request_log = request_log

    def health(self) -> HealthResponse:
        return HealthResponse(status="ok")

    def providers(self) -> ProvidersResponse:
        return ProvidersResponse(providers=tuple(self._registry.providers()))

    def authenticate_logs(self, limit: int = 100) -> AuditResponse:
        return self.audit_logs(limit)

    def audit_logs(self, limit: int = 100) -> AuditResponse:
        if self._request_log is None:
            return AuditResponse(entries=())
        return AuditResponse(entries=tuple(self._request_log.entries(limit)))

    def authenticate_request(
        self,
        request: AuthenticateRequest,
    ) -> AuthenticateResponse:
        request_id = uuid4().hex[:8]
        started = perf_counter()
        try:
            result = self._registry.authenticate(
                request.provider,
                request.identification,
                request.credential,
            )
        except UnknownProviderError:
            self._log_invocation(
                capability="authenticate",
                provider=self._log_provider(request.provider),
                identifier=request.identification.identifier,
                credential_type=request.credential.type,
                authenticated=False,
                status="unknown_provider",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
                error="unknown_provider",
            )
            raise
        except AuthenticationRejected:
            self._log_invocation(
                capability="authenticate",
                provider=self._log_provider(request.provider),
                identifier=request.identification.identifier,
                credential_type=request.credential.type,
                authenticated=False,
                status="rejected",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
            )
            return AuthenticateResponse(authenticated=False)

        self._log_invocation(
            capability="authenticate",
            provider=result.provider,
            identifier=request.identification.identifier,
            credential_type=request.credential.type,
            authenticated=True,
            status="accepted",
            duration_ms=self._duration_ms(started),
            request_id=request_id,
            identity_id=result.identity.id,
        )
        return AuthenticateResponse(authenticated=True, identity=result.identity)

    def resolve_identity_request(
        self,
        request: ResolveIdentityRequest,
    ) -> ResolveIdentityResponse:
        request_id = uuid4().hex[:8]
        started = perf_counter()
        try:
            result = self._registry.resolve_identity(
                request.provider,
                request.identification,
            )
        except UnknownProviderError:
            self._log_invocation(
                capability="resolve_identity",
                provider=self._log_provider(request.provider),
                identifier=request.identification.identifier,
                status="unknown_provider",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
                error="unknown_provider",
            )
            raise

        if result is None:
            self._log_invocation(
                capability="resolve_identity",
                provider=self._log_provider(request.provider),
                identifier=request.identification.identifier,
                status="not_found",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
            )
            return ResolveIdentityResponse(candidate=None)

        self._log_invocation(
            capability="resolve_identity",
            provider=result.provider,
            identifier=request.identification.identifier,
            candidate_id=result.candidate.implementation_id,
            status="resolved",
            duration_ms=self._duration_ms(started),
            request_id=request_id,
        )
        return ResolveIdentityResponse(candidate=result.candidate)

    def verify_credential_request(
        self,
        request: VerifyCredentialRequest,
    ) -> VerifyCredentialResponse:
        request_id = uuid4().hex[:8]
        started = perf_counter()
        try:
            result = self._registry.verify_credential(
                request.provider,
                request.candidate,
                request.credential,
            )
        except UnknownProviderError:
            self._log_invocation(
                capability="verify_credential",
                provider=self._log_provider(request.provider),
                identifier=request.candidate.identification.identifier,
                credential_type=request.credential.type,
                candidate_id=request.candidate.implementation_id,
                verified=False,
                status="unknown_provider",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
                error="unknown_provider",
            )
            raise

        self._log_invocation(
            capability="verify_credential",
            provider=result.provider,
            identifier=request.candidate.identification.identifier,
            credential_type=request.credential.type,
            candidate_id=request.candidate.implementation_id,
            verified=result.verified,
            status="verified" if result.verified else "rejected",
            duration_ms=self._duration_ms(started),
            request_id=request_id,
        )
        return VerifyCredentialResponse(verified=result.verified)

    def map_identity_request(
        self,
        request: MapIdentityRequest,
    ) -> MapIdentityResponse:
        request_id = uuid4().hex[:8]
        started = perf_counter()
        try:
            result = self._registry.map_identity(
                request.source_provider,
                request.source_identification,
                request.source_credential,
                request.target,
            )
        except UnknownProviderError:
            self._log_invocation(
                capability="map_identity",
                provider=self._log_provider(request.source_provider),
                target_provider=request.target.provider,
                identifier=request.source_identification.identifier,
                credential_type=request.source_credential.type,
                status="unknown_provider",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
                error="unknown_provider",
            )
            raise
        except AuthenticationRejected:
            self._log_invocation(
                capability="map_identity",
                provider=self._log_provider(request.source_provider),
                target_provider=request.target.provider,
                identifier=request.source_identification.identifier,
                credential_type=request.source_credential.type,
                status="rejected",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
            )
            return MapIdentityResponse(mapped=False)

        mapped = result.target_identity is not None
        self._log_invocation(
            capability="map_identity",
            provider=result.source_provider,
            target_provider=result.target_provider,
            identifier=request.source_identification.identifier,
            credential_type=request.source_credential.type,
            identity_id=result.identity.id,
            status="mapped" if mapped else "not_mapped",
            duration_ms=self._duration_ms(started),
            request_id=request_id,
        )
        return MapIdentityResponse(
            mapped=mapped,
            identity=result.identity,
            target_identity=result.target_identity,
        )

    def _log_invocation(
        self,
        *,
        capability: str,
        provider: str,
        status: str,
        duration_ms: int,
        request_id: str,
        target_provider: str | None = None,
        identifier: str | None = None,
        credential_type: str | None = None,
        candidate_id: str | None = None,
        authenticated: bool | None = None,
        verified: bool | None = None,
        identity_id: str | None = None,
        error: str | None = None,
    ) -> None:
        if self._request_log is None:
            return

        self._request_log.append_invocation(
            request_id=request_id,
            capability=capability,
            provider=provider,
            target_provider=target_provider,
            identifier=identifier,
            credential_type=credential_type,
            status=status,
            duration_ms=duration_ms,
            candidate_id=candidate_id,
            authenticated=authenticated,
            verified=verified,
            identity_id=identity_id,
            error=error,
        )

    def _duration_ms(self, started: float) -> int:
        return max(0, round((perf_counter() - started) * 1000))

    def _log_provider(self, provider: str | None) -> str:
        return provider if provider is not None else "auto"
