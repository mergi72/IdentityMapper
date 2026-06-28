from __future__ import annotations

import argparse
import http.client
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from identity_mapper.providers.basic import (
    BasicAuthenticator,
    BasicUserRecord,
    InMemoryBasicUserStore,
)
from identity_mapper_service.app import serve
from identity_mapper_service.registry import ProviderRegistry
from identity_mapper_service.request_log import RequestLog
from identity_mapper_service.service import IdentityMapperHostService


@dataclass(frozen=True, slots=True)
class HostServiceConfig:
    server: str = "127.0.0.1"
    port: int = 8066
    authenticate_log_enabled: bool = True
    authenticate_log: str = "logs/authenticate.log"


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
        port=_optional_int(value, "port", HostServiceConfig().port),
        authenticate_log_enabled=_optional_bool(
            value,
            "authenticate_log_enabled",
            HostServiceConfig().authenticate_log_enabled,
        ),
        authenticate_log=_optional_string(
            value,
            "authenticate_log",
            HostServiceConfig().authenticate_log,
        ),
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


def _optional_bool(data: dict[str, Any], key: str, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def build_demo_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    store = InMemoryBasicUserStore(
        [
            BasicUserRecord(
                implementation_id="basic:demo",
                username="demo",
                password="secret",
                identity_id="demo",
                display_name="Demo User",
                roles=("demo",),
                attributes={"source": "demo-basic"},
            )
        ]
    )
    registry.register_authenticator("basic", BasicAuthenticator(store))
    return registry


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
    serve_parser.add_argument("--authenticate-log")
    serve_parser.add_argument(
        "--disable-authenticate-log",
        action="store_true",
        help="Disable authenticate request logging for this process.",
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
        authenticate_log = args.authenticate_log or config.authenticate_log
        authenticate_log_enabled = (
            config.authenticate_log_enabled and not args.disable_authenticate_log
        )
        registry = build_demo_registry() if args.demo_basic else ProviderRegistry()
        request_log = (
            RequestLog(authenticate_log)
            if authenticate_log_enabled
            else None
        )
        service = IdentityMapperHostService(registry, request_log)
        serve(host, port, service)
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
) -> tuple[int, str, dict[str, str]]:
    connection = http.client.HTTPConnection(host, port, timeout=3)
    try:
        connection.request(method, path)
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
