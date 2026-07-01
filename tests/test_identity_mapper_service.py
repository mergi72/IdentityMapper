import http.client
import json
import threading
from datetime import datetime
from typing import Any

import pytest

from identity_mapper.providers.basic import (
    BasicAuthenticator,
    BasicCredentialVerifier,
    BasicIdentityResolver,
    BasicUserRecord,
    InMemoryBasicUserStore,
)
from identity_mapper.capabilities import Authenticate, MapIdentity, ResolveTargetIdentity
from identity_mapper.capability_protocol import (
    AuthenticateRequest,
    AuthenticateResponse,
    MapIdentityRequest,
    ResolveIdentityRequest,
    ResolveTargetIdentityRequest,
    VerifyCredentialRequest,
)
from identity_mapper.domain import (
    Credential,
    Identification,
    Identity,
    IdentityTarget,
    TargetIdentity,
    TargetIdentityResolution,
)
from identity_mapper_service.__main__ import (
    HostServiceConfig,
    build_demo_registry,
    load_config,
    main,
)
from identity_mapper_service.app import create_server
from identity_mapper_service.registry import (
    ProviderRegistry,
    UnknownProviderError,
    UnknownTargetMapperError,
    UnknownTargetResolverError,
)
from identity_mapper_service.request_log import CapabilityInvocationLog
from identity_mapper_service.responses import (
    AuditResponse,
    HealthResponse,
    ProvidersResponse,
)
from identity_mapper_service.schemas import (
    audit_response_to_mapping,
    authenticate_response_to_mapping,
    health_response_to_mapping,
    map_identity_response_to_mapping,
    resolve_identity_response_to_mapping,
    resolve_target_identity_response_to_mapping,
    verify_credential_response_to_mapping,
    providers_response_to_mapping,
)
from identity_mapper_service.service import IdentityMapperHostService


class ExampleTargetIdentityMapper(MapIdentity):
    def map_identity(
        self,
        identity: Identity,
        target: IdentityTarget,
    ) -> TargetIdentity | None:
        return TargetIdentity(
            identifier=f"{target.provider}:{identity.id}",
            target=target,
            attributes={"source": "target"},
        )


class ExampleTargetIdentityResolver(ResolveTargetIdentity):
    def __init__(self, *target_identities: TargetIdentity) -> None:
        self._known = {target_identity.identifier for target_identity in target_identities}

    def resolve_target_identity(
        self,
        target_identity: TargetIdentity,
    ) -> TargetIdentityResolution:
        exists = target_identity.identifier in self._known
        return TargetIdentityResolution(
            target_identity=target_identity,
            exists=exists,
            attributes={"lookup": "memory"} if exists else {},
        )


def make_service(request_log: CapabilityInvocationLog | None = None) -> IdentityMapperHostService:
    registry = ProviderRegistry()
    store = InMemoryBasicUserStore(
        [
            BasicUserRecord(
                implementation_id="basic:subject",
                username="subject",
                password="accepted",
                identity_id="identity-1",
                display_name="Example Subject",
                roles=("reader",),
                claims={"scope": "example"},
                attributes={"source": "basic"},
            )
        ]
    )
    registry.register_resolver("basic", BasicIdentityResolver(store))
    registry.register_verifier("basic", BasicCredentialVerifier(store))
    registry.register_authenticator("basic", BasicAuthenticator(store))
    registry.register_identity_mapper("basic", ExampleTargetIdentityMapper())
    registry.register_identity_mapper("target", ExampleTargetIdentityMapper())
    registry.register_target_resolver(
        "target",
        ExampleTargetIdentityResolver(
            TargetIdentity(
                identifier="target:identity-1",
                target=IdentityTarget(
                    provider="target",
                    realm="example",
                    purpose="bind_identity",
                ),
                attributes={"source": "target"},
            )
        ),
    )
    return IdentityMapperHostService(registry, request_log)


def valid_payload() -> dict[str, Any]:
    return {
        "provider": "basic",
        "identification": {
            "identifier": "subject",
        },
        "credential": {
            "type": "PASSWORD",
            "value": "accepted",
        },
    }


def valid_identification() -> Identification:
    return Identification(identifier="subject")


def valid_credential() -> Credential:
    return Credential(type="PASSWORD", value="accepted")


def valid_authenticate_request() -> AuthenticateRequest:
    return AuthenticateRequest(
        provider="basic",
        identification=valid_identification(),
        credential=valid_credential(),
    )


def valid_map_identity_request() -> MapIdentityRequest:
    return MapIdentityRequest(
        source_provider="basic",
        source_identification=valid_identification(),
        source_credential=valid_credential(),
        target=IdentityTarget(
            provider="target",
            realm="example",
            purpose="bind_identity",
        ),
    )


def test_service_reports_health() -> None:
    assert make_service().health() == HealthResponse(status="ok")


def test_service_reports_providers() -> None:
    assert make_service().providers() == ProvidersResponse(providers=("basic", "target"))


def test_host_service_response_mappings() -> None:
    assert health_response_to_mapping(HealthResponse(status="ok")) == {
        "status": "ok",
    }
    assert providers_response_to_mapping(
        ProvidersResponse(providers=("basic", "oauth"))
    ) == {"providers": ["basic", "oauth"]}
    assert audit_response_to_mapping(
        AuditResponse(entries=({"provider": "basic"},))
    ) == {"entries": [{"provider": "basic"}]}


def test_service_authenticates_registered_provider() -> None:
    response = make_service().authenticate_request(valid_authenticate_request())

    assert response.authenticated
    assert response.identity is not None
    assert response.identity.id == "identity-1"
    assert response.identity.display_name == "Example Subject"


def test_service_authenticates_capability_request() -> None:
    response = make_service().authenticate_request(valid_authenticate_request())

    assert response.authenticated
    assert response.identity is not None
    assert response.identity.id == "identity-1"


def test_service_can_select_provider_for_authenticate_request() -> None:
    request = AuthenticateRequest(
        identification=valid_identification(),
        credential=valid_credential(),
    )

    response = make_service().authenticate_request(request)

    assert response.authenticated
    assert response.identity is not None
    assert response.identity.id == "identity-1"


def test_service_resolves_identity_candidate() -> None:
    request = ResolveIdentityRequest(
        provider="basic",
        identification=valid_identification(),
    )

    response = make_service().resolve_identity_request(request)

    assert response.candidate is not None
    assert response.candidate.implementation_id == "basic:subject"
    assert response.candidate.identification.identifier == "subject"


def test_service_can_select_provider_for_resolve_identity_request() -> None:
    request = ResolveIdentityRequest(identification=valid_identification())

    response = make_service().resolve_identity_request(request)

    assert response.candidate is not None
    assert response.candidate.implementation_id == "basic:subject"


def test_service_returns_empty_resolution_for_unknown_identity() -> None:
    request = ResolveIdentityRequest(
        identification=Identification(identifier="missing"),
    )

    response = make_service().resolve_identity_request(request)

    assert response.candidate is None


def test_service_verifies_credential() -> None:
    candidate = make_service().resolve_identity_request(
        ResolveIdentityRequest(identification=valid_identification())
    ).candidate
    assert candidate is not None
    request = VerifyCredentialRequest(
        provider="basic",
        candidate=candidate,
        credential=valid_credential(),
    )

    response = make_service().verify_credential_request(request)

    assert response.verified


def test_service_can_select_provider_for_verify_credential_request() -> None:
    service = make_service()
    candidate = service.resolve_identity_request(
        ResolveIdentityRequest(identification=valid_identification())
    ).candidate
    assert candidate is not None
    request = VerifyCredentialRequest(
        candidate=candidate,
        credential=valid_credential(),
    )

    response = service.verify_credential_request(request)

    assert response.verified


def test_service_rejects_invalid_credential_verification() -> None:
    service = make_service()
    candidate = service.resolve_identity_request(
        ResolveIdentityRequest(identification=valid_identification())
    ).candidate
    assert candidate is not None
    request = VerifyCredentialRequest(
        candidate=candidate,
        credential=Credential(type="PASSWORD", value="wrong"),
    )

    response = service.verify_credential_request(request)

    assert not response.verified


def test_service_maps_identity_between_worlds() -> None:
    response = make_service().map_identity_request(valid_map_identity_request())

    assert response.mapped
    assert response.identity is not None
    assert response.identity.id == "identity-1"
    assert response.target_identity is not None
    assert response.target_identity.identifier == "target:identity-1"
    assert response.target_identity.target.provider == "target"


def test_service_maps_identity_to_source_world_itself() -> None:
    request = MapIdentityRequest(
        source_provider="basic",
        source_identification=valid_identification(),
        source_credential=valid_credential(),
        target=IdentityTarget(provider="basic", purpose="self"),
    )

    response = make_service().map_identity_request(request)

    assert response.mapped
    assert response.identity is not None
    assert response.identity.id == "identity-1"
    assert response.target_identity is not None
    assert response.target_identity.identifier == "basic:identity-1"
    assert response.target_identity.target.provider == "basic"


def test_service_maps_one_source_world_to_multiple_targets() -> None:
    service = make_service()
    targets = (
        IdentityTarget(provider="basic", purpose="self"),
        IdentityTarget(provider="target", purpose="foreign"),
    )

    responses = [
        service.map_identity_request(
            MapIdentityRequest(
                source_provider="basic",
                source_identification=valid_identification(),
                source_credential=valid_credential(),
                target=target,
            )
        )
        for target in targets
    ]

    assert [response.mapped for response in responses] == [True, True]
    assert [
        response.target_identity.identifier
        for response in responses
        if response.target_identity is not None
    ] == ["basic:identity-1", "target:identity-1"]


def test_service_rejects_map_identity_with_invalid_source_credential() -> None:
    class CountingTargetIdentityMapper(MapIdentity):
        calls = 0

        def map_identity(
            self,
            identity: Identity,
            target: IdentityTarget,
        ) -> TargetIdentity | None:
            self.calls += 1
            return TargetIdentity(
                identifier=f"{target.provider}:{identity.id}",
                target=target,
            )

    registry = ProviderRegistry()
    store = InMemoryBasicUserStore(
        [
            BasicUserRecord(
                implementation_id="basic:subject",
                username="subject",
                password="accepted",
                identity_id="identity-1",
            )
        ]
    )
    target_mapper = CountingTargetIdentityMapper()
    registry.register_authenticator("basic", BasicAuthenticator(store))
    registry.register_identity_mapper("target", target_mapper)
    service = IdentityMapperHostService(registry)
    request = MapIdentityRequest(
        source_provider="basic",
        source_identification=valid_identification(),
        source_credential=Credential(type="PASSWORD", value="wrong"),
        target=IdentityTarget(provider="target"),
    )

    response = service.map_identity_request(request)

    assert not response.mapped
    assert response.identity is None
    assert response.target_identity is None
    assert target_mapper.calls == 0


def test_service_rejects_unknown_target_mapper() -> None:
    request = MapIdentityRequest(
        source_provider="basic",
        source_identification=valid_identification(),
        source_credential=valid_credential(),
        target=IdentityTarget(provider="missing-target"),
    )

    with pytest.raises(UnknownTargetMapperError):
        make_service().map_identity_request(request)


def test_service_resolves_target_identity_projection() -> None:
    mapped = make_service().map_identity_request(valid_map_identity_request())
    assert mapped.target_identity is not None

    response = make_service().resolve_target_identity_request(
        ResolveTargetIdentityRequest(target_identity=mapped.target_identity)
    )

    assert response.resolved
    assert response.resolution is not None
    assert response.resolution.exists
    assert response.resolution.target_identity is mapped.target_identity
    assert response.resolution.attributes == {"lookup": "memory"}


def test_service_returns_not_found_for_missing_target_identity() -> None:
    target_identity = TargetIdentity(
        identifier="target:missing",
        target=IdentityTarget(provider="target"),
    )

    response = make_service().resolve_target_identity_request(
        ResolveTargetIdentityRequest(target_identity=target_identity)
    )

    assert not response.resolved
    assert response.resolution is not None
    assert not response.resolution.exists
    assert response.resolution.target_identity is target_identity


def test_service_rejects_unknown_target_resolver() -> None:
    target_identity = TargetIdentity(
        identifier="missing:identity",
        target=IdentityTarget(provider="missing"),
    )

    with pytest.raises(UnknownTargetResolverError):
        make_service().resolve_target_identity_request(
            ResolveTargetIdentityRequest(target_identity=target_identity)
        )


def test_authenticate_response_mapping_includes_protocol_error() -> None:
    response = AuthenticateResponse(authenticated=False, error="rejected")

    assert authenticate_response_to_mapping(response) == {
        "authenticated": False,
        "identity": None,
        "error": "rejected",
    }


def test_resolve_identity_response_mapping_includes_candidate() -> None:
    candidate = make_service().resolve_identity_request(
        ResolveIdentityRequest(identification=valid_identification())
    ).candidate
    assert candidate is not None

    assert resolve_identity_response_to_mapping(
        make_service().resolve_identity_request(
            ResolveIdentityRequest(identification=valid_identification())
        )
    ) == {
        "candidate": {
            "implementation_id": "basic:subject",
            "identification": {
                "identifier": "subject",
                "realm": None,
                "attributes": {},
            },
            "attributes": {"source": "basic"},
        },
        "error": None,
    }


def test_verify_credential_response_mapping() -> None:
    assert verify_credential_response_to_mapping(
        make_service().verify_credential_request(
            VerifyCredentialRequest(
                candidate=make_service().resolve_identity_request(
                    ResolveIdentityRequest(identification=valid_identification())
                ).candidate,
                credential=valid_credential(),
            )
        )
    ) == {"verified": True, "error": None}


def test_map_identity_response_mapping() -> None:
    response = make_service().map_identity_request(valid_map_identity_request())

    assert map_identity_response_to_mapping(response) == {
        "mapped": True,
        "identity": {
            "id": "identity-1",
            "display_name": "Example Subject",
            "email": None,
            "roles": ["reader"],
            "claims": {"scope": "example"},
            "attributes": {"source": "basic"},
        },
        "target_identity": {
            "identifier": "target:identity-1",
            "target": {
                "provider": "target",
                "realm": "example",
                "purpose": "bind_identity",
                "attributes": {},
            },
            "attributes": {"source": "target"},
        },
        "error": None,
    }


def test_resolve_target_identity_response_mapping() -> None:
    mapped = make_service().map_identity_request(valid_map_identity_request())
    assert mapped.target_identity is not None

    response = make_service().resolve_target_identity_request(
        ResolveTargetIdentityRequest(target_identity=mapped.target_identity)
    )

    assert resolve_target_identity_response_to_mapping(response) == {
        "resolved": True,
        "resolution": {
            "target_identity": {
                "identifier": "target:identity-1",
                "target": {
                    "provider": "target",
                    "realm": "example",
                    "purpose": "bind_identity",
                    "attributes": {},
                },
                "attributes": {"source": "target"},
            },
            "exists": True,
            "attributes": {"lookup": "memory"},
        },
        "error": None,
    }


def test_service_rejects_invalid_credential_without_leaking_identity() -> None:
    request = AuthenticateRequest(
        provider="basic",
        identification=valid_identification(),
        credential=Credential(type="PASSWORD", value="wrong"),
    )

    response = make_service().authenticate_request(request)

    assert not response.authenticated
    assert response.identity is None


def test_service_does_not_treat_unexpected_value_error_as_rejection() -> None:
    class BrokenAuthenticator(Authenticate):
        def authenticate(
            self,
            identification: Identification,
            credential: Credential,
        ):
            raise ValueError("unexpected failure")

    registry = ProviderRegistry()
    registry.register_authenticator("broken", BrokenAuthenticator())
    service = IdentityMapperHostService(registry)
    request = AuthenticateRequest(
        provider="broken",
        identification=valid_identification(),
        credential=valid_credential(),
    )

    with pytest.raises(ValueError, match="unexpected failure"):
        service.authenticate_request(request)


def test_service_rejects_unknown_provider() -> None:
    request = AuthenticateRequest(
        provider="missing",
        identification=valid_identification(),
        credential=valid_credential(),
    )

    with pytest.raises(UnknownProviderError):
        make_service().authenticate_request(request)


def test_http_host_validates_transport_payload() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    payload = valid_payload()
    payload["identification"] = {}

    try:
        status, response = request_json("POST", host, port, "/authenticate", payload)

        assert status == 400
        assert response["error"] == "bad_request"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_service_loads_host_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
                {
                    "server": "127.0.0.1",
                    "port": 8066,
                    "max_request_body_bytes": 4096,
                    "audit_log_enabled": False,
                    "audit_log": "logs/audit.log",
                    "audit_log_max_entries": 50,
                }
            ),
            encoding="utf-8",
    )

    assert load_config(config_path) == HostServiceConfig(
        server="127.0.0.1",
        port=8066,
        max_request_body_bytes=4096,
        audit_log_enabled=False,
        audit_log="logs/audit.log",
        audit_log_max_entries=50,
    )


def test_service_loads_legacy_authenticate_log_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "authenticate_log_enabled": False,
                "authenticate_log": "logs/authenticate.log",
                "authenticate_log_max_entries": 50,
            }
        ),
        encoding="utf-8",
    )

    assert load_config(config_path) == HostServiceConfig(
        audit_log_enabled=False,
        audit_log="logs/authenticate.log",
        audit_log_max_entries=50,
    )


def test_service_uses_default_config_when_file_is_missing(tmp_path) -> None:
    assert load_config(tmp_path / "missing.json") == HostServiceConfig()


def test_service_rejects_invalid_audit_log_enabled_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "audit_log_enabled": "false",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="audit_log_enabled"):
        load_config(config_path)


def test_service_rejects_invalid_port_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "port": 70000,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="port"):
        load_config(config_path)


def test_service_rejects_invalid_max_request_body_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "max_request_body_bytes": 0,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="max_request_body_bytes"):
        load_config(config_path)


def test_service_rejects_invalid_audit_log_max_entries_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "audit_log_max_entries": 0,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="audit_log_max_entries"):
        load_config(config_path)


def test_demo_registry_registers_basic_and_windows_target_mappers() -> None:
    registry = build_demo_registry()
    identification = Identification(identifier="demo")
    credential = Credential(type="PASSWORD", value="secret")

    basic_result = registry.map_identity(
        source_provider="basic",
        identification=identification,
        credential=credential,
        target=IdentityTarget(provider="basic", realm="local", purpose="self"),
    )
    windows_result = registry.map_identity(
        source_provider="basic",
        identification=identification,
        credential=credential,
        target=IdentityTarget(
            provider="windows",
            realm="corp.local",
            purpose="bind_identity",
        ),
    )

    assert basic_result.identity.id == "demo"
    assert basic_result.target_identity is not None
    assert basic_result.target_identity.target.provider == "basic"
    assert windows_result.identity.id == "demo"
    assert windows_result.target_identity is not None
    assert windows_result.target_identity.target.provider == "windows"
    assert windows_result.target_identity.attributes["upn_candidate"]


def test_cli_serve_rejects_invalid_max_request_body_override() -> None:
    with pytest.raises(ValueError, match="max_request_body_bytes"):
        main(["serve", "--max-request-body-bytes", "0"])


def test_cli_serve_rejects_invalid_audit_log_max_entries_override() -> None:
    with pytest.raises(ValueError, match="audit_log_max_entries"):
        main(["serve", "--audit-log-max-entries", "0"])


def test_service_can_run_without_audit_log(tmp_path) -> None:
    log_path = tmp_path / "audit.log"
    service = make_service(request_log=None)

    response = service.authenticate_request(valid_authenticate_request())

    assert response.authenticated
    assert service.authenticate_logs() == AuditResponse(entries=())
    assert not log_path.exists()


def test_service_writes_authenticate_log_without_credential_value(tmp_path) -> None:
    request_log = CapabilityInvocationLog(tmp_path / "authenticate.log")
    service = make_service(request_log)
    request = AuthenticateRequest(
        provider="basic",
        identification=valid_identification(),
        credential=Credential(type="PASSWORD", value="never-log-this-secret"),
    )

    response = service.authenticate_request(request)

    assert not response.authenticated
    entries = service.authenticate_logs().entries
    assert len(entries) == 1
    assert entries[0]["capability"] == "authenticate"
    assert entries[0]["provider"] == "basic"
    assert entries[0]["identifier"] == "subject"
    assert entries[0]["credential_type"] == "PASSWORD"
    assert entries[0]["authenticated"] is False
    assert entries[0]["status"] == "rejected"
    assert len(entries[0]["request_id"]) == 8
    assert isinstance(entries[0]["duration_ms"], int)
    assert "value" not in entries[0]
    assert "credential" not in entries[0]

    log_text = (tmp_path / "authenticate.log").read_text(encoding="utf-8")
    assert "never-log-this-secret" not in log_text


def test_service_logs_selected_provider_for_implicit_authentication(tmp_path) -> None:
    request_log = CapabilityInvocationLog(tmp_path / "authenticate.log")
    service = make_service(request_log)
    request = AuthenticateRequest(
        identification=valid_identification(),
        credential=valid_credential(),
    )

    response = service.authenticate_request(request)

    assert response.authenticated
    entries = service.authenticate_logs().entries
    assert entries[0]["capability"] == "authenticate"
    assert entries[0]["provider"] == "basic"
    assert entries[0]["status"] == "accepted"


def test_service_logs_auto_when_no_provider_accepts_request(tmp_path) -> None:
    request_log = CapabilityInvocationLog(tmp_path / "authenticate.log")
    service = make_service(request_log)
    request = AuthenticateRequest(
        identification=valid_identification(),
        credential=Credential(type="PASSWORD", value="wrong"),
    )

    response = service.authenticate_request(request)

    assert not response.authenticated
    entries = service.authenticate_logs().entries
    assert entries[0]["capability"] == "authenticate"
    assert entries[0]["provider"] == "auto"
    assert entries[0]["status"] == "rejected"


def test_request_log_trims_to_max_entries(tmp_path) -> None:
    request_log = CapabilityInvocationLog(tmp_path / "authenticate.log", max_entries=2)

    for index in range(3):
        request_log.append_authenticate(
            request_id=f"req-{index}",
            provider="basic",
            identifier=f"subject-{index}",
            credential_type="PASSWORD",
            authenticated=True,
            status="accepted",
            duration_ms=1,
            identity_id=f"identity-{index}",
        )

    entries = request_log.entries(10)
    assert [entry["request_id"] for entry in entries] == ["req-1", "req-2"]


def test_service_logs_resolve_and_verify_invocations(tmp_path) -> None:
    request_log = CapabilityInvocationLog(tmp_path / "audit.log")
    service = make_service(request_log)

    candidate = service.resolve_identity_request(
        ResolveIdentityRequest(identification=valid_identification())
    ).candidate
    assert candidate is not None
    verified = service.verify_credential_request(
        VerifyCredentialRequest(candidate=candidate, credential=valid_credential())
    )

    assert verified.verified
    entries = service.audit_logs().entries
    assert [entry["capability"] for entry in entries] == [
        "resolve_identity",
        "verify_credential",
    ]
    assert entries[0]["status"] == "resolved"
    assert entries[0]["candidate_id"] == "basic:subject"
    assert entries[1]["status"] == "verified"
    assert entries[1]["verified"] is True
    assert entries[1]["credential_type"] == "PASSWORD"
    assert "value" not in entries[1]


def test_service_writes_authenticate_log_with_local_timezone(tmp_path) -> None:
    request_log = CapabilityInvocationLog(tmp_path / "authenticate.log")
    service = make_service(request_log)

    response = service.authenticate_request(valid_authenticate_request())

    assert response.authenticated
    timestamp = request_log.entries()[0]["timestamp"]
    logged_time = datetime.fromisoformat(timestamp)
    assert logged_time.tzinfo is not None
    assert logged_time.utcoffset() == datetime.now().astimezone().utcoffset()


def test_http_host_exposes_health_providers_and_authenticate() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        assert request_json("GET", host, port, "/health") == (
            200,
            {"status": "ok"},
        )
        assert request_json("GET", host, port, "/providers") == (
            200,
            {"providers": ["basic", "target"]},
        )
        status, payload = request_json(
            "POST",
            host,
            port,
            "/authenticate",
            valid_payload(),
        )

        assert status == 200
        assert payload["authenticated"]
        assert payload["identity"]["id"] == "identity-1"
        assert payload["error"] is None
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_can_select_provider_for_authenticate() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    payload = valid_payload()
    del payload["provider"]

    try:
        status, response = request_json("POST", host, port, "/authenticate", payload)

        assert status == 200
        assert response["authenticated"]
        assert response["identity"]["id"] == "identity-1"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_resolve_identity_and_verify_credential() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, resolved = request_json(
            "POST",
            host,
            port,
            "/resolve-identity",
            {
                "identification": {
                    "identifier": "subject",
                },
            },
        )

        assert status == 200
        assert resolved["candidate"]["implementation_id"] == "basic:subject"
        assert resolved["error"] is None

        status, verified = request_json(
            "POST",
            host,
            port,
            "/verify-credential",
            {
                "candidate": resolved["candidate"],
                "credential": {
                    "type": "PASSWORD",
                    "value": "accepted",
                },
            },
        )

        assert status == 200
        assert verified == {"verified": True, "error": None}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_returns_empty_candidate_for_unknown_identity() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, resolved = request_json(
            "POST",
            host,
            port,
            "/resolve-identity",
            {
                "provider": "basic",
                "identification": {
                    "identifier": "missing",
                },
            },
        )

        assert status == 200
        assert resolved == {"candidate": None, "error": None}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_rejects_invalid_verify_credential() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, resolved = request_json(
            "POST",
            host,
            port,
            "/resolve-identity",
            {
                "identification": {
                    "identifier": "subject",
                },
            },
        )
        assert status == 200

        status, verified = request_json(
            "POST",
            host,
            port,
            "/verify-credential",
            {
                "provider": "basic",
                "candidate": resolved["candidate"],
                "credential": {
                    "type": "PASSWORD",
                    "value": "wrong",
                },
            },
        )

        assert status == 200
        assert verified == {"verified": False, "error": None}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_map_identity() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, response = request_json(
            "POST",
            host,
            port,
            "/map-identity",
            {
                "source_provider": "basic",
                "source_identification": {
                    "identifier": "subject",
                },
                "source_credential": {
                    "type": "PASSWORD",
                    "value": "accepted",
                },
                "target": {
                    "provider": "target",
                    "realm": "example",
                    "purpose": "bind_identity",
                },
            },
        )

        assert status == 200
        assert response["mapped"]
        assert response["identity"]["id"] == "identity-1"
        assert response["target_identity"]["identifier"] == "target:identity-1"
        assert response["target_identity"]["target"]["provider"] == "target"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_resolve_target_identity() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, mapped = request_json(
            "POST",
            host,
            port,
            "/map-identity",
            {
                "source_provider": "basic",
                "source_identification": {
                    "identifier": "subject",
                },
                "source_credential": {
                    "type": "PASSWORD",
                    "value": "accepted",
                },
                "target": {
                    "provider": "target",
                    "realm": "example",
                    "purpose": "bind_identity",
                },
            },
        )
        assert status == 200

        status, response = request_json(
            "POST",
            host,
            port,
            "/resolve-target-identity",
            {
                "target_identity": mapped["target_identity"],
            },
        )

        assert status == 200
        assert response["resolved"]
        assert response["resolution"]["exists"]
        assert response["resolution"]["attributes"] == {"lookup": "memory"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_audit_logs_all_capabilities(tmp_path) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "audit.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request_json("POST", host, port, "/authenticate", valid_payload())
        status, resolved = request_json(
            "POST",
            host,
            port,
            "/resolve-identity",
            {
                "identification": {
                    "identifier": "subject",
                },
            },
        )
        assert status == 200
        request_json(
            "POST",
            host,
            port,
            "/verify-credential",
            {
                "candidate": resolved["candidate"],
                "credential": {
                    "type": "PASSWORD",
                    "value": "accepted",
                },
            },
        )
        status, mapped = request_json(
            "POST",
            host,
            port,
            "/map-identity",
            {
                "source_identification": {
                    "identifier": "subject",
                },
                "source_credential": {
                    "type": "PASSWORD",
                    "value": "accepted",
                },
                "target": {
                    "provider": "target",
                },
            },
        )
        assert status == 200
        request_json(
            "POST",
            host,
            port,
            "/resolve-target-identity",
            {
                "target_identity": mapped["target_identity"],
            },
        )

        status, audit = request_json("GET", host, port, "/audit?format=json&limit=5")

        assert status == 200
        assert [entry["capability"] for entry in audit["entries"]] == [
            "authenticate",
            "resolve_identity",
            "verify_credential",
            "map_identity",
            "resolve_target_identity",
        ]
        assert audit["entries"][-1]["target_mapper"] == "target"
        assert audit["entries"][-1]["resolved"]
        assert audit["entries"][-1]["target_identity_id"] == "target:identity-1"
        assert "value" not in json.dumps(audit)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_rejects_too_large_json_body() -> None:
    service = make_service()
    server = create_server(
        "127.0.0.1",
        0,
        service,
        max_request_body_bytes=10,
    )
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, payload = request_json(
            "POST",
            host,
            port,
            "/authenticate",
            valid_payload(),
        )

        assert status == 413
        assert payload["error"] == "payload_too_large"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_uses_neutral_server_header() -> None:
    service = make_service()
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, _, headers = request_raw_with_headers("GET", host, port, "/health")

        assert status == 200
        assert headers["Server"].startswith("IdentityMapperHostService ")
        assert "IdentityMapperHostService/0.1" not in headers["Server"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_authenticate_logs(tmp_path) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, payload = request_json(
            "POST",
            host,
            port,
            "/authenticate",
            valid_payload(),
        )
        assert status == 200
        assert payload["authenticated"]

        status, body = request_raw("GET", host, port, "/authenticate_logs?limit=1")
        text = body.decode("utf-8")

        assert status == 200
        assert "<table>" in text
        assert "<th>request_id</th>" in text
        assert "<th>timestamp</th>" in text
        assert "<th>duration_ms</th>" in text
        assert "<td>basic</td>" in text
        assert "<td>subject</td>" in text
        assert "<td>PASSWORD</td>" in text
        assert "<td>accepted</td>" in text
        assert "value" not in text
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_shows_latest_authenticate_log_first(tmp_path) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        first = valid_payload()
        first["credential"]["type"] = "FIRST"
        second = valid_payload()
        second["credential"]["type"] = "SECOND"

        request_json("POST", host, port, "/authenticate", first)
        request_json("POST", host, port, "/authenticate", second)

        status, body = request_raw("GET", host, port, "/authenticate_logs?limit=2")
        text = body.decode("utf-8")

        assert status == 200
        assert text.index("<td>SECOND</td>") < text.index("<td>FIRST</td>")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_refreshes_authenticate_logs_with_html_meta(tmp_path) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        status, body, headers = request_raw_with_headers(
            "GET",
            host,
            port,
            "/authenticate_logs",
        )
        text = body.decode("utf-8")

        assert status == 200
        assert "Refresh" not in headers
        assert headers["Content-Type"] == "text/html; charset=utf-8"
        assert '<meta http-equiv="refresh" content="2">' in text
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_authenticate_logs_as_json(tmp_path) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request_json(
            "POST",
            host,
            port,
            "/authenticate",
            valid_payload(),
        )

        status, logs = request_json(
            "GET",
            host,
            port,
            "/authenticate_logs?format=json",
        )

        assert status == 200
        assert logs["entries"][0]["provider"] == "basic"
        assert logs["entries"][0]["identity_id"] == "identity-1"
        assert len(logs["entries"][0]["request_id"]) == 8
        assert isinstance(logs["entries"][0]["duration_ms"], int)
        assert "value" not in logs["entries"][0]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_authenticate_logs_as_text(tmp_path) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request_json(
            "POST",
            host,
            port,
            "/authenticate",
            valid_payload(),
        )

        status, body = request_raw("GET", host, port, "/authenticate_logs?format=text")
        text = body.decode("utf-8")
        lines = text.splitlines()
        header = lines[0]

        assert status == 200
        assert header.startswith(
            "request_id  timestamp                         capability"
        )
        assert "duration_ms" in header
        assert "authenticate" in lines[1]
        assert "basic" in lines[1]
        assert "subject" in lines[1]
        assert "PASSWORD" in lines[1]
        assert "True" in lines[1]
        assert "accepted  identity-1" in lines[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_audit_alias(tmp_path) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request_json(
            "POST",
            host,
            port,
            "/authenticate",
            valid_payload(),
        )

        status, html = request_raw("GET", host, port, "/audit?limit=1")
        assert status == 200
        assert "<td>basic</td>" in html.decode("utf-8")

        status, logs = request_json("GET", host, port, "/audit?format=json&limit=1")
        assert status == 200
        assert logs["entries"][0]["provider"] == "basic"

        status, text = request_raw("GET", host, port, "/audit?format=text&limit=1")
        assert status == 200
        audit_text = text.decode("utf-8")
        assert "basic" in audit_text
        assert "subject" in audit_text
        assert "PASSWORD" in audit_text
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_lists_providers(tmp_path, capsys) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        assert main(["providers", "--host", host, "--port", str(port)]) == 0

        assert capsys.readouterr().out == "basic\ntarget\n"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_prints_logs(tmp_path, capsys) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request_json("POST", host, port, "/authenticate", valid_payload())

        assert main(
            [
                "logs",
                "--host",
                host,
                "--port",
                str(port),
                "--limit",
                "1",
            ]
        ) == 0

        output = capsys.readouterr().out
        assert "request_id" in output
        assert "duration_ms" in output
        assert "basic" in output
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_authenticates(tmp_path, capsys) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        assert main(
            [
                "authenticate",
                "--host",
                host,
                "--port",
                str(port),
                "--provider",
                "basic",
                "--identifier",
                "subject",
                "--credential-type",
                "PASSWORD",
                "--credential-value",
                "accepted",
            ]
        ) == 0

        output = capsys.readouterr().out
        assert "authenticated=True" in output
        assert "identity_id=identity-1" in output
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_authenticate_can_defer_provider_selection(tmp_path, capsys) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        assert main(
            [
                "authenticate",
                "--host",
                host,
                "--port",
                str(port),
                "--identifier",
                "subject",
                "--credential-type",
                "PASSWORD",
                "--credential-value",
                "accepted",
            ]
        ) == 0

        output = capsys.readouterr().out
        assert "authenticated=True" in output
        assert "identity_id=identity-1" in output
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_authenticate_rejects_invalid_credential(tmp_path, capsys) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        assert main(
            [
                "authenticate",
                "--host",
                host,
                "--port",
                str(port),
                "--provider",
                "basic",
                "--identifier",
                "subject",
                "--credential-type",
                "PASSWORD",
                "--credential-value",
                "wrong",
            ]
        ) == 1

        assert "authenticated=False" in capsys.readouterr().out
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_authenticate_prints_json(tmp_path, capsys) -> None:
    service = make_service(CapabilityInvocationLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        assert main(
            [
                "authenticate",
                "--host",
                host,
                "--port",
                str(port),
                "--provider",
                "basic",
                "--identifier",
                "subject",
                "--credential-value",
                "accepted",
                "--format",
                "json",
            ]
        ) == 0

        payload = json.loads(capsys.readouterr().out)
        assert payload["authenticated"] is True
        assert payload["identity"]["id"] == "identity-1"
        assert payload["error"] is None
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request_json(
    method: str,
    host: str,
    port: int,
    path: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    body = None if payload is None else json.dumps(payload)
    headers = {"Content-Type": "application/json"} if body is not None else {}
    connection = http.client.HTTPConnection(host, port, timeout=5)
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        return response.status, data
    finally:
        connection.close()


def request_raw(
    method: str,
    host: str,
    port: int,
    path: str,
) -> tuple[int, bytes]:
    connection = http.client.HTTPConnection(host, port, timeout=5)
    try:
        connection.request(method, path)
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


def request_raw_with_headers(
    method: str,
    host: str,
    port: int,
    path: str,
) -> tuple[int, bytes, dict[str, str]]:
    connection = http.client.HTTPConnection(host, port, timeout=5)
    try:
        connection.request(method, path)
        response = connection.getresponse()
        headers = {name: value for name, value in response.getheaders()}
        return response.status, response.read(), headers
    finally:
        connection.close()
