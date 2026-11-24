# ADR-0008: Logs carry metadata only, never complaint text

- **Status:** Accepted · 2026-11-24

## Context
Logs are widely accessible and long-lived. Redaction is imperfect (names and addresses are not covered),
so even redacted text may still hold personal information.

## Decision
Log id, status, category, confidence, abstain reason, priority, hardship flag and a count of redactions.
Never log complaint text, raw or redacted. Storage errors are logged with detail but returned to
clients as a generic 503.

## Alternatives considered
- Log redacted text for debugging: leaks any PII the redactor misses.

## Consequences
+ A smaller blast radius if log access is wider than database access.
- Debugging a misclassification means looking up the record by id.
