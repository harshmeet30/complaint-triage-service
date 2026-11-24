"""End-to-end demo against an in-memory store. No server, network or credentials needed.

python scripts/demo.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("LOG_LEVEL", "WARNING")  # keep demo output readable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from triage.api import create_app  # noqa: E402
from triage.store import Store  # noqa: E402

CASES = [
    (
        "1. Scam complaint containing PII (redacted, high priority, 30-day clock)",
        {
            "text": (
                "Scam! Unauthorised charge on card 4111 1111 1111 1111. Call me on 0412 345 678."
            ),
            "received_date": "2026-03-01",
        },
    ),
    (
        "2. Hardship complaint (21-day clock)",
        {
            "text": "I lost my job and cannot afford my repayments. I need hardship help.",
            "received_date": "2026-03-01",
        },
    ),
    (
        "3. Vague complaint from a bereaved customer (safe abstain, high priority)",
        {
            "text": "My husband died last month and I need someone to call me back.",
            "received_date": "2026-03-01",
        },
    ),
    (
        "4. Invalid input (rejected with 422, nothing stored)",
        {"text": "too short"},
    ),
]

SHOW = (
    "status",
    "category",
    "confidence",
    "abstain_reason",
    "priority",
    "hardship",
    "due_date",
    "vulnerability_flags",
    "redacted_text",
)


def main() -> None:
    client = TestClient(create_app(Store(":memory:")))
    for title, payload in CASES:
        print(f"\n--- {title}")
        r = client.post("/complaints", json=payload)
        print(f"HTTP {r.status_code}")
        body = r.json()
        if r.status_code == 201:
            print(json.dumps({k: body[k] for k in SHOW}, indent=2))
        else:
            print(json.dumps(body["detail"][0]["msg"]))
    print("\n--- Review queue (abstained complaints, earliest deadline first)")
    for q in client.get("/review-queue").json():
        print(
            f"{q['id'][:8]}  due {q['due_date']}  priority={q['priority']}  "
            f"reason={q['abstain_reason']}  flags={q['vulnerability_flags']}"
        )


if __name__ == "__main__":
    main()
