from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from identity_mapper.domain import Credential, Identification, Identity
from identity_mapper.capability_protocol import (
    AuthenticateRequest,
    AuthenticateResponse,
)
from identity_mapper_service.responses import (
    AuditResponse,
    HealthResponse,
    ProvidersResponse,
)


class RequestValidationError(ValueError):
    """Raised when transport input cannot be mapped to domain input."""


def identification_from_mapping(value: Any) -> Identification:
    data = _require_mapping(value, "identification")
    return Identification(
        identifier=_require_string(data, "identifier"),
        realm=_optional_string(data, "realm"),
        attributes=_optional_dict(data, "attributes"),
    )


def credential_from_mapping(value: Any) -> Credential:
    data = _require_mapping(value, "credential")
    return Credential(
        type=_require_string(data, "type"),
        value=_require_string(data, "value"),
        metadata=_optional_dict(data, "metadata"),
    )


def authenticate_request_from_mapping(value: Any) -> AuthenticateRequest:
    data = _require_mapping(value, "request")
    provider = _require_string(data, "provider")
    return AuthenticateRequest(
        provider=provider,
        identification=identification_from_mapping(data.get("identification")),
        credential=credential_from_mapping(data.get("credential")),
    )


def identity_to_mapping(identity: Identity) -> dict[str, Any]:
    return {
        "id": identity.id,
        "display_name": identity.display_name,
        "email": identity.email,
        "roles": list(identity.roles),
        "claims": dict(identity.claims),
        "attributes": dict(identity.attributes),
    }


def authenticate_response_to_mapping(
    response: AuthenticateResponse,
) -> dict[str, Any]:
    return {
        "authenticated": response.authenticated,
        "identity": (
            identity_to_mapping(response.identity)
            if response.identity is not None
            else None
        ),
        "error": response.error,
    }


def health_response_to_mapping(response: HealthResponse) -> dict[str, Any]:
    return {"status": response.status}


def providers_response_to_mapping(response: ProvidersResponse) -> dict[str, Any]:
    return {"providers": list(response.providers)}


def audit_response_to_mapping(response: AuditResponse) -> dict[str, Any]:
    return {"entries": list(response.entries)}


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RequestValidationError(f"{field} must be an object")
    return value


def _require_string(data: Mapping[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise RequestValidationError(f"{field} must be a non-empty string")
    return value


def _optional_string(data: Mapping[str, Any], field: str) -> str | None:
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise RequestValidationError(f"{field} must be a string")
    return value


def _optional_dict(data: Mapping[str, Any], field: str) -> dict[str, Any]:
    value = data.get(field, {})
    if not isinstance(value, dict):
        raise RequestValidationError(f"{field} must be an object")
    return dict(value)
