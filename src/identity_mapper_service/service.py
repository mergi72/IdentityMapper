from __future__ import annotations

from typing import Any

from identity_mapper_service.registry import ProviderRegistry, UnknownProviderError
from identity_mapper_service.schemas import (
    RequestValidationError,
    credential_from_mapping,
    identification_from_mapping,
    identity_to_mapping,
)


class IdentityMapperHostService:
    """Host facade for IdentityMapper capabilities."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def providers(self) -> dict[str, list[str]]:
        return {"providers": list(self._registry.providers())}

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
            raise
        except ValueError:
            return {
                "authenticated": False,
                "identity": None,
            }

        return {
            "authenticated": True,
            "identity": identity_to_mapping(identity),
        }
