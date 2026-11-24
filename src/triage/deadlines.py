"""ASIC RG 271 IDR response deadlines (calendar days from receipt).

Standard complaints: 30 days. Hardship / default-notice complaints: 21 days.
Business-day and public-holiday handling is out of scope (see evidence/intent.md).
"""

from __future__ import annotations

from datetime import date, timedelta

STANDARD_DAYS = 30
HARDSHIP_DAYS = 21


def response_days(*, hardship: bool) -> int:
    return HARDSHIP_DAYS if hardship else STANDARD_DAYS


def due_date(received: date, *, hardship: bool) -> date:
    return received + timedelta(days=response_days(hardship=hardship))
