"""Triage workflow: redact -> classify -> prioritise -> deadline. Pure and side-effect free."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .classifier import Classification, classify
from .deadlines import due_date
from .redaction import redact

HIGH_PRIORITY_CATEGORIES = {"scam_fraud", "financial_hardship"}


@dataclass(frozen=True)
class TriageResult:
    redacted_text: str
    redaction_counts: dict[str, int]
    classification: Classification
    priority: str  # high | medium | low
    status: str  # triaged | needs_review
    hardship: bool
    received_date: date
    due_date: date


def triage(text: str, received: date) -> TriageResult:
    red = redact(text)
    # Classify the redacted text so downstream components never see raw PII.
    cls = classify(red.text)

    # Conservative: a financial-difficulty indicator gets the 21-day hardship clock
    # even when the category itself was abstained.
    hardship = cls.category == "financial_hardship" or "financial_difficulty" in (
        cls.vulnerability_flags
    )

    if cls.category in HIGH_PRIORITY_CATEGORIES or cls.vulnerability_flags:
        priority = "high"
    elif cls.abstained:
        priority = "medium"
    elif cls.category == "fees_charges":
        priority = "low"
    else:
        priority = "medium"

    return TriageResult(
        redacted_text=red.text,
        redaction_counts=red.counts,
        classification=cls,
        priority=priority,
        status="needs_review" if cls.abstained else "triaged",
        hardship=hardship,
        received_date=received,
        due_date=due_date(received, hardship=hardship),
    )
