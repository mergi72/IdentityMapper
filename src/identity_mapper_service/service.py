from __future__ import annotations

from typing import Any

from identity_mapper.requests import AuthenticateRequest
from identity_mapper.responses import AuthenticateResponse
from identity_mapper_service.registry import ProviderRegistry, UnknownProviderError
from identity_mapper_service.schemas import (
    authenticate_request_from_mapping,
    authenticate_response_to_mapping,
)
from identity_mapper_service.request_log import RequestLog


class IdentityMapperHostService:
    """Host facade for IdentityMapper capabilities."""

    def __init__(
        self,
        registry: ProviderRegistry,
        request_log: RequestLog | None = None,
    ) -> None:
        self._registry = registry
        self._request_log = request_log

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def providers(self) -> dict[str, list[str]]:
        return {"providers": list(self._registry.providers())}

    def authenticate_logs(self, limit: int = 100) -> dict[str, list[dict[str, Any]]]:
        if self._request_log is None:
            return {"entries": []}
        return {"entries": self._request_log.entries(limit)}

    def authenticate(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.authenticate_request(
            authenticate_request_from_mapping(payload),
        )
        return authenticate_response_to_mapping(response)

    def authenticate_request(
        self,
        request: AuthenticateRequest,
    ) -> AuthenticateResponse:
        try:
            identity = self._registry.authenticate(
                request.provider,
                request.identification,
                request.credential,
            )
        except UnknownProviderError:
            self._log_authenticate(
                provider=request.provider,
                identifier=request.identification.identifier,
                credential_type=request.credential.type,
                authenticated=False,
                status="unknown_provider",
                error="unknown_provider",
            )
            raise
        except ValueError:
            self._log_authenticate(
                provider=request.provider,
                identifier=request.identification.identifier,
                credential_type=request.credential.type,
                authenticated=False,
                status="rejected",
            )
            return AuthenticateResponse(authenticated=False)

        self._log_authenticate(
            provider=request.provider,
            identifier=request.identification.identifier,
            credential_type=request.credential.type,
            authenticated=True,
            status="accepted",
            identity_id=identity.id,
        )
        return AuthenticateResponse(authenticated=True, identity=identity)

    def _log_authenticate(
        self,
        *,
        provider: str,
        identifier: str,
        credential_type: str,
        authenticated: bool,
        status: str,
        identity_id: str | None = None,
        error: str | None = None,
    ) -> None:
        if self._request_log is None:
            return

        self._request_log.append_authenticate(
            provider=provider,
            identifier=identifier,
            credential_type=credential_type,
            authenticated=authenticated,
            status=status,
            identity_id=identity_id,
            error=error,
        )
