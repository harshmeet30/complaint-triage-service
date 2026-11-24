# Verification

## Run it
```bash
python scripts/verify.py
```
Runs four steps in order and stops on the first failure: `ruff check`, `ruff format --check`, `pytest`
with branch coverage (floor 95%), and the eval gates.

## Latest result (local, Python 3.11)
- **Lint and format:** clean.
- **Tests:** 55 passed.
- **Coverage:** 99.5% with branch coverage on (floor 95%). The only uncovered line is the
  `raise SystemExit(main(...))` entry point in `evaluate.py`. Coverage was 87% before 14 tests were added
  for the store error paths, priority branches and eval CLI (ADR-0016).
- **Eval:** 59 cases, all four gates pass.

| Eval gate | Result | Threshold |
|---|---|---|
| Accuracy on answered cases | 1.000 | ≥ 0.85 |
| Abstain rate | 0.203 | ≤ 0.25 |
| Abstain recall on designed-ambiguous cases | 1.000 | ≥ 0.75 |
| Scam/hardship confidently misrouted | 0 | = 0 |

## What is tested
| Area | Tests | Success criteria |
|---|---|---|
| PII redaction (each pattern, Luhn, no false positives, counts) | `test_redaction.py` | S2 |
| Classifier, abstain reasons, vulnerability flags | `test_classifier_deadlines.py` | S4 |
| RG 271 deadlines (30 and 21 days, year boundary) | `test_classifier_deadlines.py` | S6 |
| End-to-end API, review queue ordering | `test_api.py` | S1, S4 |
| Validation rejection with no side effects (6 cases) | `test_api.py` | S3 |
| No raw PII in response, DB or logs | `test_api.py` | S2 |
| Storage failure gives a generic 503 and a log line, health degraded | `test_api.py` | failure handling |
| Eval harness passes on the shipped set and fails on bad data | `test_evaluate.py` | S5, S7 |

## Local vs pipeline
| Check | Local | PR / pipeline |
|---|---|---|
| `scripts/verify.py` (lint, format, tests + coverage, eval) | yes | yes, as the `verify` job on push to `main` and `dev`, and on PRs to `main` |
| `scripts/demo.py` | yes | not run |
| Required-status branch protection | n/a | repository setting, not in code |

## Known gaps
- **Eval bias:** the lexicon and the eval set were written by the same author (an AI agent, with human
  direction) in one session, and the lexicon was not tuned to the eval. 100% accuracy is optimistic and
  says little about real complaints. A held-out set from independent authors is the next step (ADR-0011).
- **Eval conflates the abstain rate with the set's design:** 8 of 59 cases are designed to be ambiguous,
  so the 20% abstain figure partly reflects that mix.
- **Four labelled cases abstained** for lack of lexicon coverage:
  - "A payment went to a crypto exchange which I never authorised."
  - "Tap and pay stopped working on my debit card."
  - "Account keeping charges were deducted after I closed the account."
  - "Someone rang pretending to be from your fraud team..." (mixed signals)
  These are safe failures (a human sees them), and show where the lexicon is thin.
- **Redaction gaps:** names, addresses and free-form identifiers are not covered. Phone and account
  patterns are Australian formats only.
- **Coverage is not assertion quality.** 99.5% shows code was executed, not that it was checked well.
  The PII-leak test and the tests that make the eval gates fail are the ones that carry real weight.
- **No load, concurrency or security testing**, and no property-based or fuzz tests for the regexes.
- **CI has not been exercised on a pull request yet**, and branch protection is not configured by code.
- **No test of the real uvicorn process in CI.** The server was smoke-tested manually once.
