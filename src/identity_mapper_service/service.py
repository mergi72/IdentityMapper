from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from identity_mapper.capability_protocol import (
    AuthenticationRejected,
    AuthenticateRequest,
    AuthenticateResponse,
)
from identity_mapper_service.registry import ProviderRegistry, UnknownProviderError
from identity_mapper_service.request_log import RequestLog
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
        request_log: RequestLog | None = None,
    ) -> None:
        self._registry = registry
        self._request_log = request_log

    def health(self) -> HealthResponse:
        return HealthResponse(status="ok")

    def providers(self) -> ProvidersResponse:
        return ProvidersResponse(providers=tuple(self._registry.providers()))

    def authenticate_logs(self, limit: int = 100) -> AuditResponse:
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
            self._log_authenticate(
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
            self._log_authenticate(
                provider=self._log_provider(request.provider),
                identifier=request.identification.identifier,
                credential_type=request.credential.type,
                authenticated=False,
                status="rejected",
                duration_ms=self._duration_ms(started),
                request_id=request_id,
            )
            return AuthenticateResponse(authenticated=False)

        self._log_authenticate(
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

    def _log_authenticate(
        self,
        *,
        provider: str,
        identifier: str,
        credential_type: str,
        authenticated: bool,
        status: str,
        duration_ms: int,
        request_id: str,
        identity_id: str | None = None,
        error: str | None = None,
    ) -> None:
        if self._request_log is None:
            return

        self._request_log.append_authenticate(
            request_id=request_id,
            provider=provider,
            identifier=identifier,
            credential_type=credential_type,
            authenticated=authenticated,
            status=status,
            duration_ms=duration_ms,
            identity_id=identity_id,
            error=error,
        )

    def _duration_ms(self, started: float) -> int:
        return max(0, round((perf_counter() - started) * 1000))

    def _log_provider(self, provider: str | None) -> str:
        return provider if provider is not None else "auto"
