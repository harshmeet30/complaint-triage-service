# ADR-0016: Add a branch-coverage floor, a format check and a PR template to the gate

- **Status:** Accepted · 2026-11-24

## Context
The first CI gate ran lint and tests only. The human asked whether it had proper unit tests, coverage and
linting, and whether a PR template existed. It had no coverage measure, no format check and no template.
The first coverage measurement was 87%, with untested store-error paths, priority branches and the
eval CLI.

## Decision
- `verify.py` now runs: `ruff check`, `ruff format --check`, pytest with **branch coverage and a 95%
  floor**, then the eval gates. CI runs the same command and uploads `coverage.xml` as an artifact.
- Close the gaps with tests (not `# pragma: no cover` or omits): 14 tests added, coverage 87% to 99.5%.
- Add `.github/pull_request_template.md` with a verification, safety/privacy, ADR and AI-assistance
  checklist.

## Alternatives considered
- 100% floor: brittle, and it pushes people to write tests for `if __name__ == "__main__"` lines.
- Line coverage only: misses untested branches such as error handlers.
- Excluding hard-to-test files: hides exactly the failure paths that matter most.

## Consequences
+ A regression in coverage or formatting fails the PR. The PR template prompts for ADRs and PII checks.
- Coverage measures execution, not assertion quality. The PII-leak and gate-failure tests are the
  meaningful ones, and the number alone proves little.
- The 95% floor is a judgement call and should be revisited as the code grows.
