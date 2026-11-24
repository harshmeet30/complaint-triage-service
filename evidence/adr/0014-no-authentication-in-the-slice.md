# ADR-0014: No authentication or authorisation in the slice

- **Status:** Accepted (deliberate gap) · 2026-11-24

## Context
The exercise is a thin vertical slice, and the core path must run with no credentials or identity provider.

## Decision
The API is unauthenticated and intended for local use only. The README and `design.md` state this
prominently, with the production design: OIDC via the enterprise IdP, role-based access (handler vs
team lead vs auditor), and an audit log of reads.

## Alternatives considered
- Static API key: gives false assurance and adds setup for assessors.

## Consequences
+ Simple to run and review.
- Must not be deployed or exposed as is. This is the first thing to add for production.
