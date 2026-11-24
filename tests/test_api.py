import logging
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from triage.api import create_app
from triage.store import Store, StoreError

SCAM = "I was scammed. Unauthorised transfers I did not make left my account."
HARDSHIP = "I lost my job and cannot afford my repayments. I need hardship help."
VAGUE = "Hello, I would like to talk to someone about my situation please."


@pytest.fixture
def store():
    return Store(":memory:")


@pytest.fixture
def client(store):
    return TestClient(create_app(store))


def test_end_to_end_scam_is_high_priority_30_day(client):
    r = client.post("/complaints", json={"text": SCAM, "received_date": "2026-03-01"})
    assert r.status_code == 201
    body = r.json()
    assert body["category"] == "scam_fraud" and body["priority"] == "high"
    assert body["status"] == "triaged" and body["due_date"] == "2026-03-31"
    got = client.get(f"/complaints/{body['id']}")
    assert got.status_code == 200 and got.json()["id"] == body["id"]


def test_hardship_gets_21_day_deadline(client):
    body = client.post("/complaints", json={"text": HARDSHIP, "received_date": "2026-03-01"}).json()
    assert body["category"] == "financial_hardship" and body["hardship"] is True
    assert body["due_date"] == "2026-03-22"


def test_abstain_routes_to_review_queue(client):
    body = client.post("/complaints", json={"text": VAGUE}).json()
    assert body["abstained"] is True and body["category"] is None
    assert body["status"] == "needs_review"
    queue = client.get("/review-queue").json()
    assert [q["id"] for q in queue] == [body["id"]]


def test_vulnerable_abstained_complaint_is_high_priority(client):
    text = "My husband died last month and I need someone to call me back."
    body = client.post("/complaints", json={"text": text}).json()
    assert body["abstained"] and body["priority"] == "high"


def test_review_queue_ordered_by_due_date(client):
    old = (date.today() - timedelta(days=10)).isoformat()
    a = client.post("/complaints", json={"text": VAGUE}).json()
    b = client.post("/complaints", json={"text": VAGUE, "received_date": old}).json()
    assert [q["id"] for q in client.get("/review-queue").json()] == [b["id"], a["id"]]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"text": "short"},
        {"text": "x" * 5001},
        {"text": "valid length text here\x00nul"},
        {"text": SCAM, "received_date": (date.today() + timedelta(days=1)).isoformat()},
        {"text": SCAM, "received_date": "not-a-date"},
    ],
)
def test_invalid_input_rejected_with_no_side_effects(client, store, payload):
    r = client.post("/complaints", json=payload)
    assert r.status_code == 422
    assert store.review_queue() == [] and store.dump_text() == "[]"


def test_unknown_id_404(client):
    assert client.get("/complaints/doesnotexist").status_code == 404


def test_no_raw_pii_in_response_db_or_logs(client, store, caplog):
    pii = ["jane.doe@example.com", "4111 1111 1111 1111", "0412 345 678", "062-000", "12345678"]
    text = (
        f"Scam! Unauthorised charge on card {pii[1]}. Email {pii[0]}, phone {pii[2]}, "
        f"BSB {pii[3]} account number {pii[4]}."
    )
    with caplog.at_level(logging.DEBUG, logger="triage"):
        r = client.post("/complaints", json={"text": text})
    assert r.status_code == 201
    surfaces = {"response": r.text, "db": store.dump_text(), "logs": caplog.text}
    for name, blob in surfaces.items():
        for p in pii:
            assert p not in blob, f"raw PII {p!r} leaked into {name}"
    assert r.json()["redaction_counts"]["CARD"] == 1


def test_storage_failure_returns_generic_503_and_logs(client, store, monkeypatch, caplog):
    def boom(_):
        raise StoreError("disk I/O error at /secret/path")

    monkeypatch.setattr(store, "save", boom)
    with caplog.at_level(logging.ERROR, logger="triage"):
        r = client.post("/complaints", json={"text": SCAM})
    assert r.status_code == 503
    assert "secret" not in r.text and r.json()["detail"] == "storage unavailable, retry later"
    assert "event=store_error" in caplog.text


def test_health_ok_and_degraded(client, store, monkeypatch):
    assert client.get("/health").json() == {"status": "ok"}
    monkeypatch.setattr(store, "ping", lambda: False)
    r = client.get("/health")
    assert r.status_code == 503 and r.json() == {"status": "degraded"}
