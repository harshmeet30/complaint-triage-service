"""PII redaction. Runs before anything is stored or logged.

Covers: emails, TFNs, labelled account numbers, payment card numbers (Luhn-checked),
BSBs and Australian phone numbers. Names and addresses are NOT covered (known gap).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_TFN = re.compile(r"(?i)\b((?:tfn|tax file number)\b\D{0,15})(\d{3}[ -]?\d{3}[ -]?\d{3})\b")
_ACCOUNT = re.compile(
    r"(?i)\b((?:account|acct|a/c)\s*(?:number|no\.?|#)?\s*(?:is|:)?\s*)(\d[\d ]{4,12}\d)\b"
)
_CARD = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")
_BSB = re.compile(r"\b\d{3}-\d{3}\b")
_PHONE = re.compile(r"(?:(?:\+61|\b0)[\s-]?\(?[2-478]\)?|\(0[2-478]\))(?:[\s-]?\d){8}\b")


@dataclass(frozen=True)
class RedactionResult:
    text: str
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def luhn_valid(digits: str) -> bool:
    nums = [int(c) for c in digits if c.isdigit()]
    if not 13 <= len(nums) <= 19:
        return False
    total = 0
    for i, n in enumerate(reversed(nums)):
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def redact(text: str) -> RedactionResult:
    counts: Counter[str] = Counter()

    def sub_simple(pattern: re.Pattern[str], label: str, s: str) -> str:
        def repl(_m: re.Match[str]) -> str:
            counts[label] += 1
            return f"[{label}]"

        return pattern.sub(repl, s)

    def sub_labelled(pattern: re.Pattern[str], label: str, s: str) -> str:
        def repl(m: re.Match[str]) -> str:
            counts[label] += 1
            return f"{m.group(1)}[{label}]"

        return pattern.sub(repl, s)

    def card_repl(m: re.Match[str]) -> str:
        if luhn_valid(m.group(0)):
            counts["CARD"] += 1
            return "[CARD]"
        return m.group(0)

    out = sub_simple(_EMAIL, "EMAIL", text)
    out = sub_labelled(_TFN, "TFN", out)
    out = sub_labelled(_ACCOUNT, "ACCOUNT", out)
    out = _CARD.sub(card_repl, out)
    out = sub_simple(_BSB, "BSB", out)
    out = sub_simple(_PHONE, "PHONE", out)
    return RedactionResult(text=out, counts=dict(counts))
