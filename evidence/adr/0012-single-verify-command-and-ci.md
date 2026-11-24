# ADR-0012: One verify command shared by local development and CI

- **Status:** Accepted · 2026-11-24

## Context
Checks that only run in CI get skipped locally, and checks defined twice drift apart.

## Decision
`python scripts/verify.py` runs lint, tests and the eval. The GitHub Actions workflow runs exactly that
command on pushes to `main` and `dev` and on pull requests into `main`. The recommended branch rule is to
require the `verify` check on `main`.

## Alternatives considered
- Makefile: not available by default on Windows.
- Separate CI steps per tool: duplicates what developers run.

## Consequences
+ "Passes locally" means "passes in CI".
- Branch protection is a repository setting and cannot be committed to the repo.
