# ADR-0009: Fail closed on storage errors with a generic 503

- **Status:** Accepted · 2026-11-24

## Context
If persistence fails, accepting the complaint silently would lose a regulated record. Leaking error
detail (paths, SQL) to callers is a security risk.

## Decision
Any `StoreError` returns 503 with a fixed message and no detail. Nothing is acknowledged as triaged
unless it was saved. `/health` returns 503 `degraded` when the database can't be reached.

## Alternatives considered
- Queue in memory and acknowledge: risks silent loss on restart.

## Consequences
+ No complaint is acknowledged without being stored. The failure path is tested.
- Callers must retry. A production design would use a durable queue or outbox (see `operate.md`).
