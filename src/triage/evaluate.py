"""Evaluation harness over a labelled synthetic set.

    python -m triage.evaluate [path] [--verbose]      (run with PYTHONPATH=src)

Labels are a category name, or "needs_review" when the correct behaviour is to abstain.
Exits non-zero if any gate fails, so it can run in CI.

Gates (see evidence/intent.md S5):
  accuracy            >= 0.85  of non-abstained predictions that match the label (labelled cases)
  abstain_rate        <= 0.25  of all cases
  safe_abstain_recall >= 0.75  of "needs_review" cases that the classifier abstained on
  critical_misroutes  == 0     scam/hardship cases confidently put in a different category
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .classifier import classify

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "sample-data" / "eval_complaints.jsonl"
CRITICAL = {"scam_fraud", "financial_hardship"}

GATES = {
    "accuracy": (">=", 0.85),
    "abstain_rate": ("<=", 0.25),
    "safe_abstain_recall": (">=", 0.75),
    "critical_misroutes": ("==", 0),
}


@dataclass
class EvalReport:
    total: int = 0
    metrics: dict[str, float] = field(default_factory=dict)
    gates: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    abstained_labelled: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(self.gates.values())


def _check(value: float, op: str, bound: float) -> bool:
    return {">=": value >= bound, "<=": value <= bound, "==": value == bound}[op]


def load(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    for r in rows:
        if not {"text", "expected"} <= r.keys():
            raise ValueError(f"bad eval row: {r}")
    return rows


def evaluate(rows: list[dict]) -> EvalReport:
    rep = EvalReport(total=len(rows))
    answered = correct = abstained = 0
    review_total = review_abstained = misroutes = 0

    for r in rows:
        c = classify(r["text"])
        exp = r["expected"]
        abstained += c.abstained
        if exp == "needs_review":
            review_total += 1
            review_abstained += c.abstained
            if not c.abstained:
                rep.errors.append(f"should abstain but said {c.category}: {r['text']}")
            continue
        if c.abstained:
            rep.abstained_labelled.append(f"[{exp}] abstained ({c.abstain_reason}): {r['text']}")
            continue
        answered += 1
        if c.category == exp:
            correct += 1
        else:
            rep.errors.append(f"expected {exp}, got {c.category}: {r['text']}")
            if exp in CRITICAL:
                misroutes += 1

    rep.metrics = {
        "accuracy": correct / answered if answered else 0.0,
        "abstain_rate": abstained / len(rows) if rows else 0.0,
        "safe_abstain_recall": review_abstained / review_total if review_total else 1.0,
        "critical_misroutes": misroutes,
    }
    rep.gates = {k: _check(rep.metrics[k], *GATES[k]) for k in GATES}
    return rep


def main(argv: list[str]) -> int:
    verbose = "--verbose" in argv
    paths = [a for a in argv if not a.startswith("--")]
    rows = load(Path(paths[0]) if paths else DEFAULT_PATH)
    rep = evaluate(rows)

    print(f"eval cases: {rep.total}")
    for k, (op, bound) in GATES.items():
        v = rep.metrics[k]
        shown = f"{v:.3f}" if isinstance(v, float) and k != "critical_misroutes" else f"{v:g}"
        print(f"  {k:22s} {shown:>7s}  (gate {op} {bound})  {'PASS' if rep.gates[k] else 'FAIL'}")
    if rep.errors or verbose:
        print("misclassified:" if rep.errors else "no misclassifications")
        for e in rep.errors:
            print("  -", e)
    if verbose and rep.abstained_labelled:
        print("abstained on labelled cases (safe, but reduces automation):")
        for e in rep.abstained_labelled:
            print("  -", e)
    print("EVAL PASSED" if rep.passed else "EVAL FAILED")
    return 0 if rep.passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
