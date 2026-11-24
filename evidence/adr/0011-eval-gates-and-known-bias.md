# ADR-0011: Eval harness with four gates, and an explicit statement of its bias

- **Status:** Accepted · 2026-11-24

## Context
A classifier needs a measurable bar, and in this domain not all errors cost the same.

## Decision
A labelled synthetic set (59 cases, including 8 designed-ambiguous) with CI gates:
- accuracy on answered cases ≥ 0.85;
- abstain rate ≤ 0.25;
- abstain recall on ambiguous cases ≥ 0.75;
- zero scam/hardship cases confidently put in another category.

The harness is part of `verify.py`, and tests prove it fails when gates are breached.

## Alternatives considered
- Accuracy only: hides the unsafe-confident-error case.

## Consequences
+ The abstain trade-off is measured, not assumed.
- **Known bias:** the lexicon and the eval set were written by the same author in the same session
  (with AI assistance), and the lexicon was not tuned to the results. 100% accuracy is therefore optimistic.
  The next step is a held-out set written independently.
