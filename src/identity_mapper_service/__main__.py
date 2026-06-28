from __future__ import annotations

import argparse
import json
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
from identity_mapper_service.service import IdentityMapperHostService


@dataclass(frozen=True, slots=True)
class HostServiceConfig:
    server: str = "127.0.0.1"
    port: int = 8066


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
    serve_parser.add_argument(
        "--demo-basic",
        action="store_true",
        help="Register an in-memory Basic provider for local experiments.",
    )

    args = parser.parse_args(argv)

    if args.command == "serve":
        config = load_config(args.config)
        host = args.host or config.server
        port = args.port or config.port
        registry = build_demo_registry() if args.demo_basic else ProviderRegistry()
        service = IdentityMapperHostService(registry)
        serve(host, port, service)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
