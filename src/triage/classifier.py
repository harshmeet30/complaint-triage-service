"""Deterministic, explainable complaint classifier with a safe-abstain path.

Weighted phrase lexicon per category. Confidence is margin-based:
    confidence = top / (top + runner_up + 1)
The classifier ABSTAINS (routes to human review) when there is no signal, the top score is weak,
or confidence is below ABSTAIN_THRESHOLD. Vulnerability flags are detected independently so they
still apply when the category is abstained.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ABSTAIN_THRESHOLD = 0.6
MIN_TOP_SCORE = 2.0

LEXICON: dict[str, dict[str, float]] = {
    "scam_fraud": {
        "scam": 3, "scammed": 3, "fraud": 3, "fraudulent": 3, "unauthorised": 3,
        "unauthorized": 3, "did not authorise": 3, "didn't authorise": 3, "phishing": 3,
        "impersonat": 3, "hacked": 2, "stolen": 2, "i did not make": 3, "suspicious": 1,
    },
    "financial_hardship": {
        "hardship": 3, "can't afford": 3, "cannot afford": 3, "unable to pay": 3,
        "lost my job": 3, "redundant": 2, "repayments": 1, "default notice": 3,
        "behind on": 2, "struggling to pay": 3, "payment arrangement": 2, "arrears": 2,
    },
    "fees_charges": {
        "fee": 2, "fees": 2, "charged": 1, "overdrawn": 2, "overdraft": 2, "dishonour": 2,
        "monthly account fee": 3, "interest charge": 2, "refund the fee": 3, "fee waived": 3,
    },
    "service_conduct": {
        "rude": 3, "staff": 1, "branch": 1, "waited": 1, "hung up": 2, "call centre": 1,
        "unhelpful": 2, "poor service": 3, "discriminat": 3, "ignored": 1, "no one called": 2,
    },
    "product_issue": {
        "app": 1, "login": 2, "locked out": 3, "online banking": 2, "card declined": 3,
        "transfer failed": 3, "not working": 2, "error": 1, "glitch": 2, "payment failed": 3,
    },
}

VULNERABILITY: dict[str, list[str]] = {
    "family_violence": ["domestic violence", "family violence", "abusive partner", "afraid of my"],
    "bereavement": ["passed away", "my husband died", "my wife died", "bereavement", "funeral"],
    "health": ["hospital", "cancer", "chemotherapy", "mental health", "surgery", "illness"],
    "elderly": ["pensioner", "i am 80", "i'm 80", "aged care", "elderly"],
    "financial_difficulty": ["lost my job", "can't afford", "cannot afford", "unable to pay",
                              "hardship", "struggling to pay"],
}


@dataclass(frozen=True)
class Classification:
    category: str | None  # None when abstained
    confidence: float
    abstained: bool
    abstain_reason: str | None
    matched_terms: tuple[str, ...]
    vulnerability_flags: tuple[str, ...]
    scores: dict[str, float]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("’", "'"))


def detect_vulnerability(text: str) -> tuple[str, ...]:
    t = _norm(text)
    return tuple(flag for flag, terms in VULNERABILITY.items() if any(k in t for k in terms))


def classify(text: str) -> Classification:
    t = _norm(text)
    scores: dict[str, float] = {}
    matched: list[str] = []
    for cat, terms in LEXICON.items():
        s = 0.0
        for term, w in terms.items():
            if term in t:
                s += w
                matched.append(f"{cat}:{term}")
        scores[cat] = s

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    (top_cat, top), (_, second) = ranked[0], ranked[1]
    confidence = round(top / (top + second + 1.0), 3) if top > 0 else 0.0
    flags = detect_vulnerability(text)

    reason = None
    if top == 0:
        reason = "no_signal"
    elif top < MIN_TOP_SCORE:
        reason = "weak_signal"
    elif confidence < ABSTAIN_THRESHOLD:
        reason = "ambiguous_categories"

    return Classification(
        category=None if reason else top_cat,
        confidence=confidence,
        abstained=reason is not None,
        abstain_reason=reason,
        matched_terms=tuple(matched),
        vulnerability_flags=flags,
        scores=scores,
    )
