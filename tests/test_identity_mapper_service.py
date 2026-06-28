import http.client
import json
import threading
from datetime import datetime
from typing import Any

import pytest

from identity_mapper.providers.basic import (
    BasicAuthenticator,
    BasicUserRecord,
    InMemoryBasicUserStore,
)
from identity_mapper.domain import Credential, Identification
from identity_mapper.requests import AuthenticateRequest
from identity_mapper.responses import AuthenticateResponse
from identity_mapper_service.__main__ import HostServiceConfig, load_config, main
from identity_mapper_service.app import create_server
from identity_mapper_service.registry import ProviderRegistry, UnknownProviderError
from identity_mapper_service.request_log import RequestLog
from identity_mapper_service.schemas import authenticate_response_to_mapping
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


def test_service_reports_health() -> None:
    assert make_service().health() == {"status": "ok"}


def test_service_reports_providers() -> None:
    assert make_service().providers() == {"providers": ["basic"]}


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


def test_authenticate_response_mapping_includes_protocol_error() -> None:
    response = AuthenticateResponse(authenticated=False, error="rejected")

    assert authenticate_response_to_mapping(response) == {
        "authenticated": False,
        "identity": None,
        "error": "rejected",
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
                "authenticate_log_enabled": False,
                "authenticate_log": "logs/authenticate.log",
            }
        ),
        encoding="utf-8",
    )

    assert load_config(config_path) == HostServiceConfig(
        server="127.0.0.1",
        port=8066,
        authenticate_log_enabled=False,
        authenticate_log="logs/authenticate.log",
    )


def test_service_uses_default_config_when_file_is_missing(tmp_path) -> None:
    assert load_config(tmp_path / "missing.json") == HostServiceConfig()


def test_service_rejects_invalid_authenticate_log_enabled_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "authenticate_log_enabled": "false",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="authenticate_log_enabled"):
        load_config(config_path)


def test_service_can_run_without_authenticate_log(tmp_path) -> None:
    log_path = tmp_path / "authenticate.log"
    service = make_service(request_log=None)

    response = service.authenticate_request(valid_authenticate_request())

    assert response.authenticated
    assert service.authenticate_logs() == {"entries": []}
    assert not log_path.exists()


def test_service_writes_authenticate_log_without_credential_value(tmp_path) -> None:
    request_log = RequestLog(tmp_path / "authenticate.log")
    service = make_service(request_log)
    request = AuthenticateRequest(
        provider="basic",
        identification=valid_identification(),
        credential=Credential(type="PASSWORD", value="never-log-this-secret"),
    )

    response = service.authenticate_request(request)

    assert not response.authenticated
    entries = service.authenticate_logs()["entries"]
    assert len(entries) == 1
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


def test_service_writes_authenticate_log_with_local_timezone(tmp_path) -> None:
    request_log = RequestLog(tmp_path / "authenticate.log")
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
        assert payload["error"] is None
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
    service = make_service(RequestLog(tmp_path / "authenticate.log"))
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
    service = make_service(RequestLog(tmp_path / "authenticate.log"))
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
    service = make_service(RequestLog(tmp_path / "authenticate.log"))
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
    service = make_service(RequestLog(tmp_path / "authenticate.log"))
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
            "request_id  timestamp                         provider"
        )
        assert "duration_ms" in header
        assert "basic     subject     PASSWORD         True" in lines[1]
        assert "accepted  identity-1" in lines[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_host_exposes_audit_alias(tmp_path) -> None:
    service = make_service(RequestLog(tmp_path / "authenticate.log"))
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
        assert "basic     subject     PASSWORD" in text.decode("utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_lists_providers(tmp_path, capsys) -> None:
    service = make_service(RequestLog(tmp_path / "authenticate.log"))
    server = create_server("127.0.0.1", 0, service)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        assert main(["providers", "--host", host, "--port", str(port)]) == 0

        assert capsys.readouterr().out == "basic\n"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_prints_logs(tmp_path, capsys) -> None:
    service = make_service(RequestLog(tmp_path / "authenticate.log"))
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
