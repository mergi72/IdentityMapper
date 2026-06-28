from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from identity_mapper_service.registry import UnknownProviderError
from identity_mapper_service.schemas import RequestValidationError
from identity_mapper_service.service import IdentityMapperHostService


class JsonRequestError(ValueError):
    """Raised when an HTTP request cannot be decoded as JSON."""


def create_server(
    host: str,
    port: int,
    service: IdentityMapperHostService,
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), create_handler(service))


def serve(
    host: str,
    port: int,
    service: IdentityMapperHostService,
) -> None:
    server = create_server(host, port, service)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def create_handler(
    service: IdentityMapperHostService,
) -> type[BaseHTTPRequestHandler]:
    class IdentityMapperRequestHandler(BaseHTTPRequestHandler):
        server_version = "IdentityMapperHostService/0.1"

        def do_GET(self) -> None:
            if self.path == "/health":
                self._send_json(200, service.health())
                return

            if self.path == "/providers":
                self._send_json(200, service.providers())
                return

            self._send_json(404, {"error": "not_found"})

        def do_POST(self) -> None:
            if self.path != "/authenticate":
                self._send_json(404, {"error": "not_found"})
                return

            try:
                payload = self._read_json()
                self._send_json(200, service.authenticate(payload))
            except RequestValidationError as exc:
                self._send_json(400, {"error": "bad_request", "message": str(exc)})
            except UnknownProviderError as exc:
                self._send_json(404, {"error": "unknown_provider", "message": str(exc)})
            except JsonRequestError as exc:
                self._send_json(400, {"error": "bad_json", "message": str(exc)})

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            try:
                value = json.loads(raw_body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise JsonRequestError("request body must be JSON") from exc

            if not isinstance(value, dict):
                raise JsonRequestError("request body must be a JSON object")

            return value

        def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return IdentityMapperRequestHandler
