# Decisions

One Architecture Decision Record per significant decision, in `evidence/adr/`. Each states context, the
decision, alternatives considered and consequences (including what was intentionally not built).

| ADR | Decision | Status |
|-----|----------|--------|
| [0001](adr/0001-solution-choice-complaint-triage.md) | Build a complaint-triage service | Accepted |
| [0002](adr/0002-rules-based-classifier-over-llm.md) | Rules-based classifier instead of an LLM | Accepted |
| [0003](adr/0003-redact-pii-before-classify-store-log.md) | Redact PII before classify, store and log | Accepted |
| [0004](adr/0004-abstain-policy-and-threshold.md) | Abstain on weak or ambiguous signals (threshold 0.6) | Accepted |
| [0005](adr/0005-conservative-hardship-deadline.md) | 21-day clock whenever financial difficulty is indicated | Accepted |
| [0006](adr/0006-vulnerability-flags-drive-priority.md) | Vulnerability flags independent of category, force high priority | Accepted |
| [0007](adr/0007-python-fastapi-sqlite-stack.md) | Python, FastAPI and SQLite | Accepted |
| [0008](adr/0008-logs-carry-metadata-only.md) | Logs carry metadata only | Accepted |
| [0009](adr/0009-fail-closed-generic-503.md) | Fail closed on storage errors with a generic 503 | Accepted |
| [0010](adr/0010-input-validation-reject-early.md) | Reject invalid input at the edge | Accepted |
| [0011](adr/0011-eval-gates-and-known-bias.md) | Eval gates and the stated bias of the eval set | Accepted |
| [0012](adr/0012-single-verify-command-and-ci.md) | One verify command for local and CI | Accepted |
| [0013](adr/0013-branching-and-history-policy.md) | `dev` to `main`, no squash, AI use disclosed in docs | Accepted |
| [0014](adr/0014-no-authentication-in-the-slice.md) | No authentication in the slice (deliberate gap) | Accepted |
| [0015](adr/0015-synthetic-data-only.md) | Synthetic data only | Accepted |
| [0016](adr/0016-quality-gates-coverage-format-pr-template.md) | Coverage floor, format check and PR template | Accepted |

## Intentionally not built
Authentication, channel ingestion, business-day and holiday calendars, NER for names and addresses,
a raw-text vault, an LLM classifier, cloud deployment, and a durable queue. Each is covered in the
relevant ADR or in `design.md`.

New decisions get the next number. A reversed decision is marked *Superseded by ADR-00NN* rather than edited.
