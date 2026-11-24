"""HTTP API. Run: uvicorn triage.api:app --app-dir src

Config (env): TRIAGE_DB (default data/triage.db), LOG_LEVEL (default INFO).
No secrets are required.
"""

from __future__ import annotations

import logging
import os
from datetime import date

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from .service import triage
from .store import Store, StoreError

log = logging.getLogger("triage")

MAX_TEXT = 5000
MIN_TEXT = 10


class ComplaintIn(BaseModel):
    text: str = Field(description="Free-text complaint (synthetic data only)")
    received_date: date | None = Field(default=None, description="Defaults to today (UTC)")

    @field_validator("text")
    @classmethod
    def _check_text(cls, v: str) -> str:
        v = v.strip()
        if "\x00" in v:
            raise ValueError("text must not contain NUL characters")
        if not MIN_TEXT <= len(v) <= MAX_TEXT:
            raise ValueError(f"text must be {MIN_TEXT}-{MAX_TEXT} characters")
        return v

    @field_validator("received_date")
    @classmethod
    def _not_future(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("received_date must not be in the future")
        return v


def _public(row: dict) -> dict:
    return {
        "id": row["id"],
        "status": row["status"],
        "category": row["category"],
        "confidence": row["confidence"],
        "abstained": row["abstained"],
        "abstain_reason": row["abstain_reason"],
        "priority": row["priority"],
        "hardship": row["hardship"],
        "received_date": row["received_date"],
        "due_date": row["due_date"],
        "vulnerability_flags": row["vulnerability_flags"],
        "matched_terms": row["matched_terms"],
        "redacted_text": row["redacted_text"],
        "redaction_counts": row["redaction_counts"],
    }


def create_app(store: Store | None = None) -> FastAPI:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app = FastAPI(title="Complaint Triage Service", version="0.1.0")
    state: dict[str, Store | None] = {"store": store}

    def get_store() -> Store:
        if state["store"] is None:
            state["store"] = Store(os.environ.get("TRIAGE_DB", "data/triage.db"))
        return state["store"]

    @app.exception_handler(StoreError)
    async def _store_error(_: Request, exc: StoreError) -> JSONResponse:
        # Detail goes to logs only; the client gets a generic message.
        log.error("event=store_error detail=%s", exc)
        return JSONResponse(status_code=503, content={"detail": "storage unavailable, retry later"})

    @app.get("/health")
    def health() -> JSONResponse:
        try:
            ok = get_store().ping()
        except StoreError:
            ok = False
        return JSONResponse(
            status_code=200 if ok else 503, content={"status": "ok" if ok else "degraded"}
        )

    @app.post("/complaints", status_code=201)
    def submit(body: ComplaintIn) -> dict:
        received = body.received_date or date.today()
        result = triage(body.text, received)
        cid = get_store().save(result)
        c = result.classification
        # Log metadata only. Never the complaint text, raw or redacted.
        log.info(
            "event=triaged id=%s status=%s category=%s confidence=%s abstain_reason=%s "
            "priority=%s hardship=%s redactions=%s",
            cid, result.status, c.category, c.confidence, c.abstain_reason,
            result.priority, result.hardship, sum(result.redaction_counts.values()),
        )
        row = get_store().get(cid)
        return _public(row)  # type: ignore[arg-type]

    @app.get("/complaints/{cid}")
    def fetch(cid: str) -> dict:
        row = get_store().get(cid)
        if row is None:
            raise HTTPException(status_code=404, detail="complaint not found")
        return _public(row)

    @app.get("/review-queue")
    def review_queue() -> list[dict]:
        return [_public(r) for r in get_store().review_queue()]

    return app


app = create_app()
