# ADR-0007: Python, FastAPI and SQLite for the local slice

- **Status:** Accepted · 2026-11-24

## Context
Assessors must run the core path from a clean checkout with no containers, credentials or services.

## Decision
FastAPI for the HTTP API, pydantic for validation, SQLite for persistence (a file, or `:memory:` in
tests), pytest and ruff for verification. Dependencies are pinned in `requirements.txt`.

## Alternatives considered
- Postgres plus Docker Compose: closer to production, but adds setup and a hard dependency on Docker.
- Serverless framework: needs cloud accounts.

## Consequences
+ `pip install` and one command to run. Fast, hermetic tests.
- SQLite is not the production shape. The store sits behind a small class, so swapping in Postgres is
  contained (see `design.md`).
