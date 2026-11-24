# ADR-0003: Redact PII at the boundary, before classification, storage and logging

- **Status:** Accepted · 2026-11-24

## Context
Free-text complaints carry card numbers, account details, phone numbers and emails. Once raw PII
reaches a database or log it spreads to backups, monitoring and support tooling.

## Decision
`service.triage()` redacts first. Everything downstream (classifier, store, API response, logs) only
sees redacted text. The raw text is never persisted. Card numbers are redacted only when they pass a
Luhn check, to avoid destroying reference numbers.

## Alternatives considered
- Store raw text encrypted: needs key management beyond the slice, and a larger breach impact.
- Redact only at display time: leaves raw PII in storage and logs.

## Consequences
+ A single choke point, enforced by a test that checks the response, the DB dump and the logs for leaks.
- The original text can't be recovered for re-triage or dispute. A production design would need a
  governed raw store with access controls and retention rules.
- Names and addresses are not redacted (known gap, needs NER).
