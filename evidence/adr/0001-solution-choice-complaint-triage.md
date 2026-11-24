# ADR-0001: Build a complaint-triage service

- **Status:** Accepted · 2026-11-24

## Context
The exercise needs a meaningful, regulated-enterprise-credible vertical slice with a guarded failure
path, built in 3 hours, runnable offline with no paid keys.

## Decision
Build a complaint-triage service: redact PII, classify, assign an ASIC RG 271 deadline, abstain to a
human when unsure.

## Alternatives considered
- Payment-instruction validator: strong on validation, but little scope for a safe-abstain path.
- Grounded policy Q&A over public documents: a common AI demo, and weaker on regulated-bank concerns.

## Consequences
+ Maps directly to real obligations (RG 271 timeframes, privacy, vulnerable customers).
+ Natural fit for an abstain path and an eval harness.
- Complaint text is sensitive in reality, so redaction must be correct (see ADR-0003).
