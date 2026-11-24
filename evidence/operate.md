# Operate

## Run
See the README. `python scripts/demo.py` for a quick look. For the server:
`PYTHONPATH=src uvicorn triage.api:app` (Windows PowerShell: `$env:PYTHONPATH="src"; uvicorn triage.api:app`).

## Config and secrets
| Variable | Default | Meaning |
|---|---|---|
| `TRIAGE_DB` | `data/triage.db` | SQLite path (`:memory:` allowed) |
| `LOG_LEVEL` | `INFO` | Python log level |

There are no secrets in the slice. In production, secrets come from a cloud secret manager and
configuration from environment variables. Nothing sensitive is committed (`.env`, `*.db` and `data/`
are git-ignored).

## Logs and status
One structured line per triage, with metadata only (ADR-0008):
```
event=triaged id=… status=needs_review category=None confidence=0.0 abstain_reason=no_signal priority=high hardship=False redactions=0
event=store_error detail=…          (ERROR; detail never returned to the client)
```
`GET /health` returns `{"status":"ok"}`, or 503 `{"status":"degraded"}` if the database can't be reached.
Useful signals to alert on in production: abstain rate, `store_error` count, 5xx rate, review-queue
age (oldest due date) and the count of complaints approaching their deadline.

## Failure modes and responses
| Failure | Behaviour | Operator action |
|---|---|---|
| Invalid input | 422, nothing stored | None, client error |
| Database unavailable or full | 503 generic, `store_error` logged, `/health` degraded, nothing acknowledged | Restore storage, clients retry |
| Classifier uncertain | Abstain, `needs_review`, queued by deadline | A handler works the review queue |
| Redactor misses a PII form | Residual PII could sit in stored text (never in logs) | Extend patterns, re-scan the store, assess under the privacy-incident process |
| Lexicon drift (accuracy falls) | Visible only through the eval or review feedback | Re-run `verify.py` with new cases, update the lexicon |

## Rollback and degrade thinking
- The service is stateless apart from the database, so rollback is a redeploy of the previous image.
- The schema is create-if-not-exists only. Production needs versioned migrations that are
  backward-compatible across one release, so a rollback never meets a schema it can't read.
- **Degrade path:** if the classifier were ever unhealthy or low-confidence, forcing everything to abstain
  routes all complaints to humans. It is slow but safe, and a one-flag change would implement it.

## Local-to-cloud: CI/CD path
1. **Pull request:** `verify` (lint, tests, eval gates) must pass, plus dependency and secret scanning,
   and at least one reviewer. Required checks are enforced by branch protection on `main`.
2. **Merge to `main`:** build a container image, tag it with the commit SHA, scan it, and push to the
   registry. Generate an SBOM.
3. **Deploy to test:** apply the Terraform for the environment, run migrations, deploy the image, and run
   a smoke test (`/health`, one synthetic complaint, one abstain, one rejection) with the synthetic
   eval set as a post-deploy check.
4. **Promote to staging, then production:** the same image, promoted by digest and never rebuilt. Use
   progressive rollout (canary), and watch the abstain rate and 5xx rate before going wider. Automatic
   rollback on SLO breach.
5. **Change control:** classifier changes (lexicon or model) are treated as a model release. They need
   eval results attached, owner approval and a compliance sign-off where regulated outcomes are affected.

## Not covered by this slice
Authentication, TLS, encryption at rest, backups and retention, rate limiting, multi-instance writes (SQLite),
schema migrations, observability stack, and an on-call runbook for the cloud environment.
