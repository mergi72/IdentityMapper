from __future__ import annotations

from typing import Any

from identity_mapper_service.registry import ProviderRegistry, UnknownProviderError
from identity_mapper_service.schemas import (
    RequestValidationError,
    credential_from_mapping,
    identification_from_mapping,
    identity_to_mapping,
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
        provider = payload.get("provider")
        if not isinstance(provider, str) or not provider:
            raise RequestValidationError("provider must be a non-empty string")

        identification = identification_from_mapping(payload.get("identification"))
        credential = credential_from_mapping(payload.get("credential"))

        try:
            identity = self._registry.authenticate(
                provider,
                identification,
                credential,
            )
        except UnknownProviderError:
            self._log_authenticate(
                provider=provider,
                identifier=identification.identifier,
                credential_type=credential.type,
                authenticated=False,
                status="unknown_provider",
                error="unknown_provider",
            )
            raise
        except ValueError:
            self._log_authenticate(
                provider=provider,
                identifier=identification.identifier,
                credential_type=credential.type,
                authenticated=False,
                status="rejected",
            )
            return {
                "authenticated": False,
                "identity": None,
            }

        self._log_authenticate(
            provider=provider,
            identifier=identification.identifier,
            credential_type=credential.type,
            authenticated=True,
            status="accepted",
            identity_id=identity.id,
        )
        return {
            "authenticated": True,
            "identity": identity_to_mapping(identity),
        }

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
