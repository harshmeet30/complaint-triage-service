from datetime import date

import pytest
from fastapi.testclient import TestClient

from triage.api import create_app
from triage.service import triage
from triage.store import Store, StoreError

D = date(2026, 3, 1)


def test_fees_complaint_is_low_priority():
    r = triage("I was charged a dishonour fee and a monthly account fee.", D)
    assert r.classification.category == "fees_charges"
    assert r.priority == "low" and r.status == "triaged" and not r.hardship


def test_product_issue_is_medium_priority():
    r = triage("I am locked out of online banking and the app shows an error.", D)
    assert r.classification.category == "product_issue" and r.priority == "medium"


def test_abstained_without_flags_is_medium_and_needs_review():
    r = triage("Hello, I would like to talk to someone about my situation.", D)
    assert r.status == "needs_review" and r.priority == "medium"


def test_classifier_sees_redacted_text_only():
    r = triage("Scam on card 4111 1111 1111 1111, email me at a@b.com", D)
    assert "4111" not in r.redacted_text and "a@b.com" not in r.redacted_text
    assert r.redaction_counts == {"EMAIL": 1, "CARD": 1}


def test_store_round_trip_preserves_types():
    store = Store(":memory:")
    cid = store.save(triage("I lost my job and cannot afford my repayments, hardship.", D))
    row = store.get(cid)
    assert row["hardship"] is True and row["abstained"] is False
    assert isinstance(row["vulnerability_flags"], list) and row["due_date"] == "2026-03-22"
    assert store.get("missing") is None and store.ping() is True


def test_store_init_failure_is_wrapped(tmp_path):
    blocker = tmp_path / "file.txt"
    blocker.write_text("x")
    with pytest.raises(StoreError):
        Store(str(blocker / "sub" / "triage.db"))


def test_store_operations_after_close_raise_store_error():
    store = Store(":memory:")
    result = triage("I was scammed, unauthorised transfers I did not make.", D)
    store._conn.close()
    assert store.ping() is False
    with pytest.raises(StoreError):
        store.save(result)
    with pytest.raises(StoreError):
        store.get("x")


def test_app_lazily_opens_db_from_env(tmp_path, monkeypatch):
    db = tmp_path / "nested" / "triage.db"
    monkeypatch.setenv("TRIAGE_DB", str(db))
    client = TestClient(create_app())
    r = client.post("/complaints", json={"text": "I was scammed, unauthorised transfers."})
    assert r.status_code == 201 and db.exists()


def test_health_degraded_when_db_cannot_open(tmp_path, monkeypatch):
    blocker = tmp_path / "file.txt"
    blocker.write_text("x")
    monkeypatch.setenv("TRIAGE_DB", str(blocker / "sub" / "triage.db"))
    client = TestClient(create_app())
    r = client.get("/health")
    assert r.status_code == 503 and r.json() == {"status": "degraded"}
