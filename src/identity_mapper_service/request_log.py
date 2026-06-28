from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class AuthenticateLogEntry:
    request_id: str
    timestamp: str
    provider: str
    identifier: str
    credential_type: str
    authenticated: bool
    status: str
    duration_ms: int
    identity_id: str | None = None
    error: str | None = None

    def to_mapping(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "provider": self.provider,
            "identifier": self.identifier,
            "credential_type": self.credential_type,
            "authenticated": self.authenticated,
            "status": self.status,
            "duration_ms": self.duration_ms,
        }
        if self.identity_id is not None:
            value["identity_id"] = self.identity_id
        if self.error is not None:
            value["error"] = self.error
        return value


class RequestLog:
    """Append-only JSONL request log for hosted capabilities."""

    def __init__(self, path: str | Path, max_entries: int = 1000) -> None:
        self._path = Path(path)
        self._max_entries = max_entries
        self._lock = threading.Lock()

    def append_authenticate(
        self,
        *,
        request_id: str,
        provider: str,
        identifier: str,
        credential_type: str,
        authenticated: bool,
        status: str,
        duration_ms: int,
        identity_id: str | None = None,
        error: str | None = None,
    ) -> None:
        entry = AuthenticateLogEntry(
            request_id=request_id,
            timestamp=datetime.now().astimezone().isoformat(),
            provider=provider,
            identifier=identifier,
            credential_type=credential_type,
            authenticated=authenticated,
            status=status,
            duration_ms=duration_ms,
            identity_id=identity_id,
            error=error,
        )
        self._append(entry.to_mapping())

    def entries(self, limit: int = 100) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        with self._lock:
            if not self._path.exists():
                return []

            lines = self._path.read_text(encoding="utf-8").splitlines()

        entries: list[dict[str, Any]] = []
        for line in lines[-limit:]:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                entries.append(value)
        return entries

    def _append(self, entry: dict[str, Any]) -> None:
        line = json.dumps(entry, sort_keys=True)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as log_file:
                log_file.write(line)
                log_file.write("\n")
            self._trim()

    def _trim(self) -> None:
        lines = self._path.read_text(encoding="utf-8").splitlines()
        if len(lines) <= self._max_entries:
            return

        self._path.write_text(
            "\n".join(lines[-self._max_entries :]) + "\n",
            encoding="utf-8",
        )
