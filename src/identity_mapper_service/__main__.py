from __future__ import annotations

import argparse

from identity_mapper.providers.basic import (
    BasicAuthenticator,
    BasicUserRecord,
    InMemoryBasicUserStore,
)
from identity_mapper_service.app import serve
from identity_mapper_service.registry import ProviderRegistry
from identity_mapper_service.service import IdentityMapperHostService


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
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8080)
    serve_parser.add_argument(
        "--demo-basic",
        action="store_true",
        help="Register an in-memory Basic provider for local experiments.",
    )

    args = parser.parse_args(argv)

    if args.command == "serve":
        registry = build_demo_registry() if args.demo_basic else ProviderRegistry()
        service = IdentityMapperHostService(registry)
        serve(args.host, args.port, service)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
