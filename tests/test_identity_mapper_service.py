import http.client
import json
import threading
from typing import Any

import pytest

from identity_mapper.providers.basic import (
    BasicAuthenticator,
    BasicUserRecord,
    InMemoryBasicUserStore,
)
from identity_mapper_service.__main__ import HostServiceConfig, load_config
from identity_mapper_service.app import create_server
from identity_mapper_service.registry import ProviderRegistry, UnknownProviderError
from identity_mapper_service.request_log import RequestLog
from identity_mapper_service.schemas import RequestValidationError
from identity_mapper_service.service import IdentityMapperHostService


def make_service(request_log: RequestLog | None = None) -> IdentityMapperHostService:
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
    registry.register_authenticator("basic", BasicAuthenticator(store))
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


def test_service_reports_health() -> None:
    assert make_service().health() == {"status": "ok"}


def test_service_reports_providers() -> None:
    assert make_service().providers() == {"providers": ["basic"]}


def test_service_authenticates_registered_provider() -> None:
    response = make_service().authenticate(valid_payload())

    assert response["authenticated"]
    assert response["identity"]["id"] == "identity-1"
    assert response["identity"]["display_name"] == "Example Subject"


def test_service_rejects_invalid_credential_without_leaking_identity() -> None:
    payload = valid_payload()
    payload["credential"]["value"] = "wrong"

    assert make_service().authenticate(payload) == {
        "authenticated": False,
        "identity": None,
    }


def test_service_rejects_unknown_provider() -> None:
    payload = valid_payload()
    payload["provider"] = "missing"

    with pytest.raises(UnknownProviderError):
        make_service().authenticate(payload)


def test_service_validates_transport_payload() -> None:
    payload = valid_payload()
    payload["identification"] = {}

    with pytest.raises(RequestValidationError):
        make_service().authenticate(payload)


def test_service_loads_host_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "server": "127.0.0.1",
                "port": 8066,
                "authenticate_log": "logs/authenticate.log",
            }
        ),
        encoding="utf-8",
    )

    assert load_config(config_path) == HostServiceConfig(
        server="127.0.0.1",
        port=8066,
        authenticate_log="logs/authenticate.log",
    )


def test_service_uses_default_config_when_file_is_missing(tmp_path) -> None:
    assert load_config(tmp_path / "missing.json") == HostServiceConfig()


def test_service_writes_authenticate_log_without_credential_value(tmp_path) -> None:
    request_log = RequestLog(tmp_path / "authenticate.log")
    service = make_service(request_log)
    payload = valid_payload()
    payload["credential"]["value"] = "never-log-this-secret"

    response = service.authenticate(payload)

    assert not response["authenticated"]
    entries = service.authenticate_logs()["entries"]
    assert len(entries) == 1
    assert entries[0]["provider"] == "basic"
    assert entries[0]["identifier"] == "subject"
    assert entries[0]["credential_type"] == "PASSWORD"
    assert entries[0]["authenticated"] is False
    assert entries[0]["status"] == "rejected"
    assert "value" not in entries[0]
    assert "credential" not in entries[0]

    log_text = (tmp_path / "authenticate.log").read_text(encoding="utf-8")
    assert "never-log-this-secret" not in log_text


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
            {"providers": ["basic"]},
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
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_authenticate_logs(tmp_path) -> None:
    service = make_service(RequestLog(tmp_path / "authenticate.log"))
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

        status, logs = request_json("GET", host, port, "/authenticate_logs?limit=1")
        assert status == 200
        assert logs["entries"][0]["provider"] == "basic"
        assert logs["entries"][0]["authenticated"] is True
        assert logs["entries"][0]["identity_id"] == "identity-1"
        assert "value" not in logs["entries"][0]
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
