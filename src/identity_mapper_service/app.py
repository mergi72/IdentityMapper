from __future__ import annotations

import json
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from typing import Any

from identity_mapper_service.registry import UnknownProviderError
from identity_mapper_service.schemas import (
    RequestValidationError,
    authenticate_request_from_mapping,
    authenticate_response_to_mapping,
    audit_response_to_mapping,
    health_response_to_mapping,
    map_identity_request_from_mapping,
    map_identity_response_to_mapping,
    providers_response_to_mapping,
    resolve_identity_request_from_mapping,
    resolve_identity_response_to_mapping,
    verify_credential_request_from_mapping,
    verify_credential_response_to_mapping,
)
from identity_mapper_service.service import IdentityMapperHostService

DEFAULT_MAX_REQUEST_BODY_BYTES = 65536


class JsonRequestError(ValueError):
    """Raised when an HTTP request cannot be decoded as JSON."""

    def __init__(
        self,
        message: str,
        *,
        error: str = "bad_json",
        status_code: int = 400,
    ) -> None:
        super().__init__(message)
        self.error = error
        self.status_code = status_code


def create_server(
    host: str,
    port: int,
    service: IdentityMapperHostService,
    max_request_body_bytes: int = DEFAULT_MAX_REQUEST_BODY_BYTES,
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(
        (host, port),
        create_handler(service, max_request_body_bytes),
    )


def serve(
    host: str,
    port: int,
    service: IdentityMapperHostService,
    max_request_body_bytes: int = DEFAULT_MAX_REQUEST_BODY_BYTES,
) -> None:
    server = create_server(host, port, service, max_request_body_bytes)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def create_handler(
    service: IdentityMapperHostService,
    max_request_body_bytes: int = DEFAULT_MAX_REQUEST_BODY_BYTES,
) -> type[BaseHTTPRequestHandler]:
    class IdentityMapperRequestHandler(BaseHTTPRequestHandler):
        server_version = "IdentityMapperHostService"

        def do_GET(self) -> None:
            url = urlparse(self.path)
            if url.path == "/health":
                self._send_json(200, health_response_to_mapping(service.health()))
                return

            if url.path == "/providers":
                self._send_json(
                    200,
                    providers_response_to_mapping(service.providers()),
                )
                return

            if url.path in {"/authenticate_logs", "/audit"}:
                try:
                    self._send_audit_logs(url.query)
                except RequestValidationError as exc:
                    self._send_error(400, "bad_request", str(exc))
                return

            self._send_error(404, "not_found", "endpoint not found")

        def do_POST(self) -> None:
            if self.path == "/authenticate":
                self._handle_authenticate()
                return

            if self.path == "/resolve-identity":
                self._handle_resolve_identity()
                return

            if self.path == "/verify-credential":
                self._handle_verify_credential()
                return

            if self.path == "/map-identity":
                self._handle_map_identity()
                return

            self._send_error(404, "not_found", "endpoint not found")

        def _handle_authenticate(self) -> None:
            try:
                payload = self._read_json()
                request = authenticate_request_from_mapping(payload)
                response = service.authenticate_request(request)
                self._send_json(200, authenticate_response_to_mapping(response))
            except RequestValidationError as exc:
                self._send_error(400, "bad_request", str(exc))
            except UnknownProviderError as exc:
                self._send_error(404, "unknown_provider", str(exc))
            except JsonRequestError as exc:
                self._send_error(exc.status_code, exc.error, str(exc))

        def _handle_map_identity(self) -> None:
            try:
                payload = self._read_json()
                request = map_identity_request_from_mapping(payload)
                response = service.map_identity_request(request)
                self._send_json(200, map_identity_response_to_mapping(response))
            except RequestValidationError as exc:
                self._send_error(400, "bad_request", str(exc))
            except UnknownProviderError as exc:
                self._send_error(404, "unknown_provider", str(exc))
            except JsonRequestError as exc:
                self._send_error(exc.status_code, exc.error, str(exc))

        def _handle_resolve_identity(self) -> None:
            try:
                payload = self._read_json()
                request = resolve_identity_request_from_mapping(payload)
                response = service.resolve_identity_request(request)
                self._send_json(200, resolve_identity_response_to_mapping(response))
            except RequestValidationError as exc:
                self._send_error(400, "bad_request", str(exc))
            except UnknownProviderError as exc:
                self._send_error(404, "unknown_provider", str(exc))
            except JsonRequestError as exc:
                self._send_error(exc.status_code, exc.error, str(exc))

        def _handle_verify_credential(self) -> None:
            try:
                payload = self._read_json()
                request = verify_credential_request_from_mapping(payload)
                response = service.verify_credential_request(request)
                self._send_json(200, verify_credential_response_to_mapping(response))
            except RequestValidationError as exc:
                self._send_error(400, "bad_request", str(exc))
            except UnknownProviderError as exc:
                self._send_error(404, "unknown_provider", str(exc))
            except JsonRequestError as exc:
                self._send_error(exc.status_code, exc.error, str(exc))

        def _read_json(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise JsonRequestError(
                    "content length must be an integer",
                    error="bad_content_length",
                ) from exc

            if length > max_request_body_bytes:
                raise JsonRequestError(
                    "request body is too large",
                    error="payload_too_large",
                    status_code=413,
                )

            raw_body = self.rfile.read(length)
            try:
                value = json.loads(raw_body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise JsonRequestError("request body must be JSON") from exc

            if not isinstance(value, dict):
                raise JsonRequestError("request body must be a JSON object")

            return value

        def _read_limit(self, query: str) -> int:
            value = parse_qs(query).get("limit", ["100"])[0]
            try:
                limit = int(value)
            except ValueError as exc:
                raise RequestValidationError("limit must be an integer") from exc
            if limit < 1 or limit > 1000:
                raise RequestValidationError("limit must be between 1 and 1000")
            return limit

        def _read_format(self, query: str) -> str:
            value = parse_qs(query).get("format", ["html"])[0]
            if value not in {"html", "json", "text"}:
                raise RequestValidationError("format must be html, json, or text")
            return value

        def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
            body = (json.dumps(payload, sort_keys=True) + "\r\n").encode("utf-8")
            self._send_response(status_code, body)

        def _send_error(
            self,
            status_code: int,
            error: str,
            message: str,
        ) -> None:
            self._send_json(
                status_code,
                {
                    "error": error,
                    "message": message,
                },
            )

        def _send_audit_logs(self, query: str) -> None:
            limit = self._read_limit(query)
            payload = audit_response_to_mapping(service.audit_logs(limit))
            output_format = self._read_format(query)
            if output_format == "json":
                self._send_json(200, payload)
            elif output_format == "text":
                self._send_audit_log_text(200, payload)
            else:
                self._send_audit_log_html(200, payload)

        def _send_audit_log_html(
            self,
            status_code: int,
            payload: dict[str, Any],
        ) -> None:
            entries = payload.get("entries", [])
            if not isinstance(entries, list):
                self._send_json(status_code, payload)
                return

            columns = self._audit_log_columns()
            rows = [
                "          <tr>"
                + "".join(
                    f"<td>{escape(self._format_log_value(entry.get(column)))}</td>"
                    for column in columns
                )
                + "</tr>"
                for entry in reversed(entries)
            ]
            empty_row = (
                f'          <tr><td colspan="{len(columns)}" class="empty">'
                "No capability invocations logged yet.</td></tr>"
            )
            body = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="2">
    <title>IdentityMapper Audit Log</title>
    <style>
      body {{
        color: #172026;
        font-family: Consolas, "Cascadia Mono", monospace;
        margin: 16px;
      }}
      table {{
        border-collapse: collapse;
        font-size: 13px;
        width: 100%;
      }}
      th, td {{
        border-bottom: 1px solid #d5dde3;
        padding: 4px 10px;
        text-align: left;
        white-space: nowrap;
      }}
      th {{
        background: #eef3f6;
        position: sticky;
        top: 0;
      }}
      .empty {{
        color: #5f6b73;
        padding: 12px 10px;
      }}
    </style>
  </head>
  <body>
    <table>
      <thead>
        <tr>{''.join(f'<th>{escape(column)}</th>' for column in columns)}</tr>
      </thead>
      <tbody>
{chr(13).join(rows) if rows else empty_row}
      </tbody>
    </table>
  </body>
</html>
"""
            self._send_response(
                status_code,
                body.encode("utf-8"),
                "text/html; charset=utf-8",
            )

        def _send_audit_log_text(
            self,
            status_code: int,
            payload: dict[str, Any],
        ) -> None:
            entries = payload.get("entries", [])
            if not isinstance(entries, list):
                self._send_json(status_code, payload)
                return

            columns = self._audit_log_columns()
            rows = [
                [self._format_log_value(entry.get(column)) for column in columns]
                for entry in entries
            ]
            widths = [
                max([len(column), *(len(row[index]) for row in rows)])
                for index, column in enumerate(columns)
            ]
            header = self._format_log_row(columns, widths)
            lines = [header]
            for index, row in enumerate(rows):
                if index > 0 and index % 20 == 0:
                    lines.append(header)
                lines.append(self._format_log_row(row, widths))
            body = ("\r\n".join(lines) + "\r\n").encode("utf-8")
            self._send_response(
                status_code,
                body,
                "text/plain; charset=utf-8",
            )

        def _audit_log_columns(self) -> tuple[str, ...]:
            return (
                "request_id",
                "timestamp",
                "capability",
                "provider",
                "target_provider",
                "identifier",
                "credential_type",
                "candidate_id",
                "authenticated",
                "verified",
                "status",
                "identity_id",
                "duration_ms",
                "error",
            )

        def _format_log_value(self, value: object) -> str:
            if value is None:
                return ""
            text = str(value)
            return text.replace("\r", " ").replace("\n", " ").replace("\t", " ")

        def _format_log_row(
            self,
            values: tuple[str, ...] | list[str],
            widths: list[int],
        ) -> str:
            return "  ".join(
                value.ljust(widths[index])
                for index, value in enumerate(values)
            ).rstrip()

        def _send_response(
            self,
            status_code: int,
            body: bytes,
            content_type: str = "application/json",
            headers: dict[str, str] | None = None,
        ) -> None:
            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for name, value in (headers or {}).items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body)

    return IdentityMapperRequestHandler
