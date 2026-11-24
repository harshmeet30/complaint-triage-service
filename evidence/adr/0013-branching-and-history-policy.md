# ADR-0013: Work on `dev`, promote to `main`, preserve history, disclose AI use in the docs

- **Status:** Accepted · 2026-11-24

## Context
The brief asks for incremental commits and forbids squashing or rewriting history.

## Decision
All work is committed in small steps on `dev` and pushed regularly. `dev` is promoted to `main` with a
merge commit or fast-forward, never a squash. Commit messages carry no AI co-author trailer, at the
repository owner's preference. AI-agent use is disclosed instead in `agentic-workflow.md` and the README.

## Alternatives considered
- Squash-merge for a tidy history: contradicts the brief.

## Consequences
+ The commit history shows how the slice was built.
- Attribution of AI assistance lives in documentation, not commit metadata, so the docs must stay accurate.
