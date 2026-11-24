"""SQLite persistence. Only REDACTED text is ever stored."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from .service import TriageResult

_SCHEMA = """
CREATE TABLE IF NOT EXISTS complaints (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    received_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    redacted_text TEXT NOT NULL,
    redaction_counts TEXT NOT NULL,
    category TEXT,
    confidence REAL NOT NULL,
    abstained INTEGER NOT NULL,
    abstain_reason TEXT,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    hardship INTEGER NOT NULL,
    vulnerability_flags TEXT NOT NULL,
    matched_terms TEXT NOT NULL
)
"""


class StoreError(Exception):
    """Raised for any persistence failure; the API maps it to a generic 503."""


class Store:
    def __init__(self, path: str = "data/triage.db") -> None:
        self._lock = threading.Lock()
        try:
            if path != ":memory:":
                import os

                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            self._conn = sqlite3.connect(path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            with self._lock:
                self._conn.execute(_SCHEMA)
                self._conn.commit()
        except (sqlite3.Error, OSError) as exc:
            raise StoreError(str(exc)) from exc

    def save(self, r: TriageResult) -> str:
        cid = uuid.uuid4().hex
        c = r.classification
        try:
            with self._lock:
                self._conn.execute(
                    "INSERT INTO complaints VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        cid,
                        datetime.now(UTC).isoformat(timespec="seconds"),
                        r.received_date.isoformat(),
                        r.due_date.isoformat(),
                        r.redacted_text,
                        json.dumps(r.redaction_counts),
                        c.category,
                        c.confidence,
                        int(c.abstained),
                        c.abstain_reason,
                        r.priority,
                        r.status,
                        int(r.hardship),
                        json.dumps(list(c.vulnerability_flags)),
                        json.dumps(list(c.matched_terms)),
                    ),
                )
                self._conn.commit()
        except sqlite3.Error as exc:
            raise StoreError(str(exc)) from exc
        return cid

    def get(self, cid: str) -> dict[str, Any] | None:
        return self._one("SELECT * FROM complaints WHERE id = ?", (cid,))

    def review_queue(self) -> list[dict[str, Any]]:
        return self._many(
            "SELECT * FROM complaints WHERE status = 'needs_review' "
            "ORDER BY due_date ASC, created_at ASC"
        )

    def dump_text(self) -> str:
        """Everything stored, as one string. Used by the PII-leak test."""
        return json.dumps(self._many("SELECT * FROM complaints"))

    def ping(self) -> bool:
        try:
            with self._lock:
                self._conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def _one(self, sql: str, params: tuple = ()) -> dict[str, Any] | None:
        rows = self._many(sql, params)
        return rows[0] if rows else None

    def _many(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        try:
            with self._lock:
                rows = self._conn.execute(sql, params).fetchall()
        except sqlite3.Error as exc:
            raise StoreError(str(exc)) from exc
        out = []
        for row in rows:
            d = dict(row)
            d["abstained"] = bool(d["abstained"])
            d["hardship"] = bool(d["hardship"])
            for k in ("redaction_counts", "vulnerability_flags", "matched_terms"):
                d[k] = json.loads(d[k])
            out.append(d)
        return out
