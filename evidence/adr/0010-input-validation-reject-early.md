# ADR-0010: Reject invalid input at the edge with 422 and no side effects

- **Status:** Accepted · 2026-11-24

## Context
Unbounded or malformed input threatens the storage, the regex-based redactor and downstream consumers.

## Decision
Pydantic validators reject text outside 10-5000 characters, text containing NUL characters, and a
`received_date` in the future. Rejection happens before triage or storage, and a test confirms nothing
is written.

## Alternatives considered
- Truncate long text silently: could cut off a complaint's key content.

## Consequences
+ Bounded work per request. Clear client errors.
- A 5000-character cap may be too tight for long emails. Make it configurable if real data needs it.
