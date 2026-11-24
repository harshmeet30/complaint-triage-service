# ADR-0015: Synthetic data only, with well-known test values

- **Status:** Accepted · 2026-11-24

## Context
The brief forbids confidential, customer or staff data, and the repo is public.

## Decision
All complaints in tests and the eval set are written by hand. Card numbers use well-known test PANs
(e.g. 4111 1111 1111 1111), and phone numbers, BSBs and accounts are fabricated. No real data enters
the repo, and the SQLite file and `data/` directory are git-ignored.

## Alternatives considered
- Scraped public complaints: licensing and privacy uncertainty.

## Consequences
+ Safe to publish and share.
- Synthetic text is cleaner than real complaints, so real-world accuracy will be lower (see ADR-0011).
