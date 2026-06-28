from __future__ import annotations

import argparse
import http.client
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from identity_mapper.providers.basic import (
    BasicAuthenticator,
    BasicCredentialVerifier,
    BasicIdentityResolver,
    BasicUserRecord,
    InMemoryBasicUserStore,
)
from identity_mapper_service.app import DEFAULT_MAX_REQUEST_BODY_BYTES, serve
from identity_mapper_service.registry import ProviderRegistry
from identity_mapper_service.request_log import CapabilityInvocationLog
from identity_mapper_service.service import IdentityMapperHostService


@dataclass(frozen=True, slots=True)
class HostServiceConfig:
    server: str = "127.0.0.1"
    port: int = 8066
    max_request_body_bytes: int = DEFAULT_MAX_REQUEST_BODY_BYTES
    audit_log_enabled: bool = True
    audit_log: str = "logs/audit.log"
    audit_log_max_entries: int = 1000
    providers: tuple[ProviderConfig, ...] = ()


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    name: str
    type: str
    enabled: bool = True
    users: tuple[BasicProviderUserConfig, ...] = ()


@dataclass(frozen=True, slots=True)
class BasicProviderUserConfig:
    username: str
    password: str
    identity_id: str
    implementation_id: str | None = None
    display_name: str | None = None
    email: str | None = None
    roles: tuple[str, ...] = ()
    claims: dict[str, Any] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)


def load_config(path: str | Path = "config/config.json") -> HostServiceConfig:
    config_path = Path(path)
    if not config_path.exists():
        return HostServiceConfig()

    with config_path.open("r", encoding="utf-8") as config_file:
        value = json.load(config_file)

    if not isinstance(value, dict):
        raise ValueError("config must be a JSON object")

    return HostServiceConfig(
        server=_optional_string(value, "server", HostServiceConfig().server),
        port=_optional_port(value, "port", HostServiceConfig().port),
        max_request_body_bytes=_optional_positive_int(
            value,
            "max_request_body_bytes",
            HostServiceConfig().max_request_body_bytes,
        ),
        audit_log_enabled=_optional_bool(
            value,
            "audit_log_enabled",
            _optional_bool(
                value,
                "authenticate_log_enabled",
                HostServiceConfig().audit_log_enabled,
            ),
        ),
        audit_log=_optional_string(
            value,
            "audit_log",
            _optional_string(
                value,
                "authenticate_log",
                HostServiceConfig().audit_log,
            ),
        ),
        audit_log_max_entries=_optional_positive_int(
            value,
            "audit_log_max_entries",
            _optional_positive_int(
                value,
                "authenticate_log_max_entries",
                HostServiceConfig().audit_log_max_entries,
            ),
        ),
        providers=_optional_providers(value, "providers"),
    )


def _optional_string(data: dict[str, Any], key: str, default: str) -> str:
    value = data.get(key, default)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _optional_int(data: dict[str, Any], key: str, default: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _optional_positive_int(data: dict[str, Any], key: str, default: int) -> int:
    value = _optional_int(data, key, default)
    if value < 1:
        raise ValueError(f"{key} must be greater than zero")
    return value


def _optional_port(data: dict[str, Any], key: str, default: int) -> int:
    value = _optional_int(data, key, default)
    if value < 1 or value > 65535:
        raise ValueError(f"{key} must be between 1 and 65535")
    return value


def _optional_bool(data: dict[str, Any], key: str, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _optional_providers(
    data: dict[str, Any],
    key: str,
) -> tuple[ProviderConfig, ...]:
    value = data.get(key, ())
    if not isinstance(value, list | tuple):
        raise ValueError(f"{key} must be a list")

    return tuple(_provider_config_from_mapping(item) for item in value)


def _provider_config_from_mapping(value: Any) -> ProviderConfig:
    if not isinstance(value, dict):
        raise ValueError("provider config must be an object")

    provider_type = _required_string(value, "type")
    if provider_type != "basic":
        raise ValueError(f"unknown provider type: {provider_type}")

    return ProviderConfig(
        name=_required_string(value, "name"),
        type=provider_type,
        enabled=_optional_bool(value, "enabled", True),
        users=_optional_basic_users(value, "users"),
    )


def _optional_basic_users(
    data: dict[str, Any],
    key: str,
) -> tuple[BasicProviderUserConfig, ...]:
    value = data.get(key, ())
    if not isinstance(value, list | tuple):
        raise ValueError(f"{key} must be a list")

    return tuple(_basic_user_config_from_mapping(item) for item in value)


def _basic_user_config_from_mapping(value: Any) -> BasicProviderUserConfig:
    if not isinstance(value, dict):
        raise ValueError("basic provider user config must be an object")

    return BasicProviderUserConfig(
        username=_required_string(value, "username"),
        password=_required_string(value, "password"),
        identity_id=_required_string(value, "identity_id"),
        implementation_id=_optional_string_or_none(value, "implementation_id"),
        display_name=_optional_string_or_none(value, "display_name"),
        email=_optional_string_or_none(value, "email"),
        roles=_optional_string_tuple(value, "roles"),
        claims=_optional_mapping(value, "claims"),
        attributes=_optional_mapping(value, "attributes"),
    )


def _required_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _optional_string_or_none(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string or null")
    return value


def _optional_string_tuple(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key, ())
    if not isinstance(value, list | tuple):
        raise ValueError(f"{key} must be a list")
    if not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return tuple(value)


def _optional_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return dict(value)


def build_configured_registry(config: HostServiceConfig) -> ProviderRegistry:
    registry = ProviderRegistry()
    for provider in config.providers:
        if not provider.enabled:
            continue
        _register_provider(registry, provider)
    return registry


def _register_provider(registry: ProviderRegistry, provider: ProviderConfig) -> None:
    if provider.type == "basic":
        _register_basic_provider(registry, provider.name, provider.users)
        return
    raise ValueError(f"unknown provider type: {provider.type}")


def build_demo_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    _register_demo_basic_provider(registry)
    return registry


def _register_demo_basic_provider(registry: ProviderRegistry) -> None:
    _register_basic_provider(
        registry,
        "basic",
        (
            BasicProviderUserConfig(
                implementation_id="basic:demo",
                username="demo",
                password="secret",
                identity_id="demo",
                display_name="Demo User",
                roles=("demo",),
                attributes={"source": "demo-basic"},
            ),
        ),
    )


def _register_basic_provider(
    registry: ProviderRegistry,
    provider_name: str,
    users: tuple[BasicProviderUserConfig, ...],
) -> None:
    store = InMemoryBasicUserStore(
        [
            BasicUserRecord(
                implementation_id=user.implementation_id
                or f"{provider_name}:{user.username}",
                username=user.username,
                password=user.password,
                identity_id=user.identity_id,
                display_name=user.display_name,
                email=user.email,
                roles=user.roles,
                claims=user.claims,
                attributes=user.attributes,
            )
            for user in users
        ]
    )
    registry.register_resolver(provider_name, BasicIdentityResolver(store))
    registry.register_verifier(provider_name, BasicCredentialVerifier(store))
    registry.register_authenticator(provider_name, BasicAuthenticator(store))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="identity_mapper_service",
        description="Host IdentityMapper capabilities through a transport.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--config", default="config/config.json")
    serve_parser.add_argument("--host")
    serve_parser.add_argument("--port", type=int)
    serve_parser.add_argument("--max-request-body-bytes", type=int)
    serve_parser.add_argument("--audit-log")
    serve_parser.add_argument("--authenticate-log", help=argparse.SUPPRESS)
    serve_parser.add_argument("--audit-log-max-entries", type=int)
    serve_parser.add_argument(
        "--authenticate-log-max-entries",
        type=int,
        help=argparse.SUPPRESS,
    )
    serve_parser.add_argument(
        "--disable-audit-log",
        action="store_true",
        help="Disable capability invocation logging for this process.",
    )
    serve_parser.add_argument(
        "--disable-authenticate-log",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    serve_parser.add_argument(
        "--demo-basic",
        action="store_true",
        help="Register an in-memory Basic provider for local experiments.",
    )

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--config", default="config/config.json")
    status_parser.add_argument("--host")
    status_parser.add_argument("--port", type=int)

    providers_parser = subparsers.add_parser("providers")
    providers_parser.add_argument("--config", default="config/config.json")
    providers_parser.add_argument("--host")
    providers_parser.add_argument("--port", type=int)

    authenticate_parser = subparsers.add_parser("authenticate")
    authenticate_parser.add_argument("--config", default="config/config.json")
    authenticate_parser.add_argument("--host")
    authenticate_parser.add_argument("--port", type=int)
    authenticate_parser.add_argument("--provider")
    authenticate_parser.add_argument("--identifier", required=True)
    authenticate_parser.add_argument("--credential-type", default="PASSWORD")
    authenticate_parser.add_argument("--credential-value", required=True)
    authenticate_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
    )

    logs_parser = subparsers.add_parser("logs")
    logs_parser.add_argument("--config", default="config/config.json")
    logs_parser.add_argument("--host")
    logs_parser.add_argument("--port", type=int)
    logs_parser.add_argument("--limit", type=int, default=100)
    logs_parser.add_argument(
        "--format",
        choices=("text", "json", "html"),
        default="text",
    )

    args = parser.parse_args(argv)

    if args.command == "serve":
        config = load_config(args.config)
        host = args.host or config.server
        port = args.port or config.port
        max_request_body_bytes = (
            args.max_request_body_bytes
            if args.max_request_body_bytes is not None
            else config.max_request_body_bytes
        )
        if max_request_body_bytes < 1:
            raise ValueError("max_request_body_bytes must be greater than zero")

        audit_log = args.audit_log or args.authenticate_log or config.audit_log
        audit_log_max_entries = (
            args.audit_log_max_entries
            if args.audit_log_max_entries is not None
            else (
                args.authenticate_log_max_entries
                if args.authenticate_log_max_entries is not None
                else config.audit_log_max_entries
            )
        )
        if audit_log_max_entries < 1:
            raise ValueError("audit_log_max_entries must be greater than zero")

        audit_log_enabled = (
            config.audit_log_enabled
            and not args.disable_audit_log
            and not args.disable_authenticate_log
        )
        registry = build_configured_registry(config)
        if args.demo_basic:
            _register_demo_basic_provider(registry)
        invocation_log = (
            CapabilityInvocationLog(audit_log, max_entries=audit_log_max_entries)
            if audit_log_enabled
            else None
        )
        service = IdentityMapperHostService(registry, invocation_log)
        serve(host, port, service, max_request_body_bytes)
        return 0

    if args.command == "status":
        config = load_config(args.config)
        host = args.host or config.server
        port = args.port or config.port
        return _status(host, port)

    if args.command == "providers":
        config = load_config(args.config)
        host = args.host or config.server
        port = args.port or config.port
        return _providers(host, port)

    if args.command == "authenticate":
        config = load_config(args.config)
        host = args.host or config.server
        port = args.port or config.port
        return _authenticate(
            host,
            port,
            args.provider,
            args.identifier,
            args.credential_type,
            args.credential_value,
            args.format,
        )

    if args.command == "logs":
        config = load_config(args.config)
        host = args.host or config.server
        port = args.port or config.port
        return _logs(host, port, args.limit, args.format)

    parser.error(f"unknown command: {args.command}")
    return 2


def _status(host: str, port: int) -> int:
    connection = http.client.HTTPConnection(host, port, timeout=3)
    try:
        connection.request("GET", "/health")
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    except OSError as exc:
        print(f"IdentityMapper Host Service is not reachable: {exc}")
        return 1
    finally:
        connection.close()

    if response.status != 200:
        print(f"IdentityMapper Host Service returned HTTP {response.status}: {body}")
        return 1

    print(f"IdentityMapper Host Service is running on {host}:{port}")
    return 0


def _providers(host: str, port: int) -> int:
    status, body, _ = _request(host, port, "GET", "/providers")
    if status != 200:
        print(f"IdentityMapper Host Service returned HTTP {status}: {body}")
        return 1

    payload = json.loads(body)
    for provider in payload.get("providers", []):
        print(provider)
    return 0


def _authenticate(
    host: str,
    port: int,
    provider: str | None,
    identifier: str,
    credential_type: str,
    credential_value: str,
    output_format: str,
) -> int:
    payload = {
        "identification": {
            "identifier": identifier,
        },
        "credential": {
            "type": credential_type,
            "value": credential_value,
        },
    }
    if provider is not None:
        payload["provider"] = provider
    status, body, headers = _request(
        host,
        port,
        "POST",
        "/authenticate",
        payload,
    )
    if status != 200:
        print(f"IdentityMapper Host Service returned HTTP {status}: {body}")
        return 1

    response = json.loads(body)
    if output_format == "json" and headers.get("Content-Type", "").startswith(
        "application/json"
    ):
        print(json.dumps(response, indent=2, sort_keys=True))
        return 0

    if response.get("authenticated"):
        identity = response.get("identity") or {}
        identity_id = identity.get("id", "")
        display_name = identity.get("display_name", "")
        print(
            "authenticated=True "
            f"identity_id={identity_id} "
            f"display_name={display_name}"
        )
        return 0

    error = response.get("error") or ""
    print(f"authenticated=False error={error}")
    return 1


def _logs(host: str, port: int, limit: int, output_format: str) -> int:
    status, body, headers = _request(
        host,
        port,
        "GET",
        f"/audit?format={output_format}&limit={limit}",
    )
    if status != 200:
        print(f"IdentityMapper Host Service returned HTTP {status}: {body}")
        return 1

    content_type = headers.get("Content-Type", "")
    if output_format == "json" and content_type.startswith("application/json"):
        print(json.dumps(json.loads(body), indent=2, sort_keys=True))
    else:
        sys.stdout.write(body)
    return 0


def _request(
    host: str,
    port: int,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, str, dict[str, str]]:
    connection = http.client.HTTPConnection(host, port, timeout=3)
    try:
        body = None if payload is None else json.dumps(payload)
        headers = {"Content-Type": "application/json"} if body is not None else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        headers = {name: value for name, value in response.getheaders()}
        return response.status, body, headers
    except OSError as exc:
        print(f"IdentityMapper Host Service is not reachable: {exc}")
        return 0, "", {}
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
