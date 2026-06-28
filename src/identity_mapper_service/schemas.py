from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityCandidate,
)
from identity_mapper.capability_protocol import (
    AuthenticateRequest,
    AuthenticateResponse,
    ResolveIdentityRequest,
    ResolveIdentityResponse,
    VerifyCredentialRequest,
    VerifyCredentialResponse,
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
    provider = _optional_non_empty_string(data, "provider")
    return AuthenticateRequest(
        identification=identification_from_mapping(data.get("identification")),
        credential=credential_from_mapping(data.get("credential")),
        provider=provider,
    )


def resolve_identity_request_from_mapping(value: Any) -> ResolveIdentityRequest:
    data = _require_mapping(value, "request")
    provider = _optional_non_empty_string(data, "provider")
    return ResolveIdentityRequest(
        identification=identification_from_mapping(data.get("identification")),
        provider=provider,
    )


def verify_credential_request_from_mapping(value: Any) -> VerifyCredentialRequest:
    data = _require_mapping(value, "request")
    provider = _optional_non_empty_string(data, "provider")
    return VerifyCredentialRequest(
        candidate=identity_candidate_from_mapping(data.get("candidate")),
        credential=credential_from_mapping(data.get("credential")),
        provider=provider,
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


def identification_to_mapping(identification: Identification) -> dict[str, Any]:
    return {
        "identifier": identification.identifier,
        "realm": identification.realm,
        "attributes": dict(identification.attributes),
    }


def identity_candidate_from_mapping(value: Any) -> IdentityCandidate:
    data = _require_mapping(value, "candidate")
    return IdentityCandidate(
        implementation_id=_require_string(data, "implementation_id"),
        identification=identification_from_mapping(data.get("identification")),
        attributes=_optional_dict(data, "attributes"),
    )


def identity_candidate_to_mapping(candidate: IdentityCandidate) -> dict[str, Any]:
    return {
        "implementation_id": candidate.implementation_id,
        "identification": identification_to_mapping(candidate.identification),
        "attributes": dict(candidate.attributes),
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


def resolve_identity_response_to_mapping(
    response: ResolveIdentityResponse,
) -> dict[str, Any]:
    return {
        "candidate": (
            identity_candidate_to_mapping(response.candidate)
            if response.candidate is not None
            else None
        ),
        "error": response.error,
    }


def verify_credential_response_to_mapping(
    response: VerifyCredentialResponse,
) -> dict[str, Any]:
    return {
        "verified": response.verified,
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


def _optional_non_empty_string(data: Mapping[str, Any], field: str) -> str | None:
    value = _optional_string(data, field)
    if value == "":
        raise RequestValidationError(f"{field} must be a non-empty string")
    return value


def _optional_dict(data: Mapping[str, Any], field: str) -> dict[str, Any]:
    value = data.get(field, {})
    if not isinstance(value, dict):
        raise RequestValidationError(f"{field} must be an object")
    return dict(value)
