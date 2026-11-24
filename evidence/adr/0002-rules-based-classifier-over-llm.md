# ADR-0002: Deterministic rules-based classifier instead of an LLM

- **Status:** Accepted · 2026-11-24

## Context
The core path must run offline with no paid keys or credentials. Decisions on complaints must be
explainable to a regulator and reproducible in tests.

## Decision
Use a weighted-phrase lexicon with margin-based confidence (`top / (top + runner_up + 1)`). Each result
records the matched terms that drove it. An LLM classifier can be added later behind the same
`classify()` interface.

## Alternatives considered
- Hosted LLM: needs credentials, is non-deterministic, and sends complaint text to a third party.
- Local small model: heavy setup for assessors, and still less explainable.
- Trained ML classifier: needs a real labelled corpus, which we don't have.

## Consequences
+ Offline, deterministic, fully testable, with an audit trail of why.
- Lower recall on unseen phrasing. Four labelled eval cases abstained for exactly this reason.
- Lexicon and eval set share an author, so measured accuracy is optimistic (see ADR-0011).
