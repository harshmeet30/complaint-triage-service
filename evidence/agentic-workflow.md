# Agentic workflow

## Tools
- **Claude Code** (CLI) was the only AI tool and the primary implementation tool. It wrote essentially
  all of the code, tests and documentation in this repository, and it ran the commands and tests.
- Models: Claude Opus 5.5 for the early phases, then Claude Sonnet 5.5 after a model switch partway
  through (phase 2 onwards).
- No other AI tools, no hosted model APIs in the product, and no private data were used.

## How the work was decomposed
Work ran in phases, with a human checkpoint after each. Each phase ended in small commits on `dev`.

| Phase | Output | Commit(s) |
|---|---|---|
| 1. Frame | `intent.md` with measurable success criteria, scaffold | `7ccea90` |
| 2. Core engine | redaction, classifier with abstain, deadlines, unit tests | `de49666`, `6c8ad15` |
| 2b. CI gate | `scripts/verify.py`, GitHub Actions | `1406176` |
| 3. Service | validation, SQLite store, FastAPI, 503 path, PII-leak test | `8cfdb7f` |
| 4. Eval | labelled set, harness with gates, wired into verify | `26db441` |
| 4b. ADRs | 15 decision records and an index | `d76ade7` |
| 5b. CI quality | coverage floor, format check, PR template, ADR-0016 | see `git log` |
| 5. Docs | README, design, verify, operate, this file | see `git log` |

Success criteria were written first, so each phase had a testable target (`intent.md` S1-S7).

## Where the human steered
These changes came from the person directing the work, not from the agent:
- **Solution choice:** picked complaint triage from three options the agent proposed.
- **Repository hygiene:** asked for the repo to be named for the project, with no employer name in it.
- **Branching:** asked for work to happen on a `dev` branch, promoted to `main` later (ADR-0013).
- **CI first:** asked "did we add a CI gate before going further?" The agent had not, and added it
  before the service layer was built (`1406176`).
- **ADRs:** asked for a decision record for every decision, not the 3-5 the brief suggests. The agent
  had planned to write only a short `decisions.md`.
- **CI quality:** asked whether CI had proper unit tests, coverage and linting, and a PR template. The
  agent had added lint and tests only. Coverage measured 87%, and the agent closed the gaps with tests
  rather than exclusions, then added the format check, a 95% floor and the template (ADR-0016).
- **Diagrams:** asked for an architecture and flow diagram in the README. The agent's first README
  draft had none. It was rejected and rewritten with Mermaid request-flow, component and delivery diagrams.
- **Attribution:** instructed that commits must not carry an AI co-author trailer. The agent had added
  one in its first commit attempt, the human rejected that command, and the commit was redone without it.
  AI use is disclosed here and in the README instead (ADR-0013).

## Representative steering prompts
- "go" after each checkpoint (phase gate).
- "lets create a new repo with the name of project dont add [employer] name to the repo name"
- "can you create a dev branch first for these changes and then we can later promote to the main"
- "did we add ci gate before going further?"
- "did you add the adrs, I want adrs for every decision"
- "for the ci did we add proper unit tests, coverage test and a lint tester, plus do we have a PR template"

## How output was reviewed and verified
- **Tests first on risk:** PII leakage is tested across the response, database and logs together.
  Failure paths (422, 503, abstain) each have a test.
- **Gates that can fail:** the eval harness has tests that feed it deliberately wrong data and check
  that it fails (`tests/test_evaluate.py`), so it can't pass vacuously.
- **Real run, not only tests:** the agent started the actual server and made an HTTP request
  after phase 3, and ran `scripts/demo.py` for the README example.
- **Honest limits recorded:** the agent flagged, and the docs state, that it wrote the lexicon and the
  eval set together, so measured accuracy is optimistic (ADR-0011). The lexicon was not tuned to the eval.
- **Linting and one command:** `python scripts/verify.py` is the single check, locally and in CI.

## Where AI output needed correction or was weak
- The agent's first commit command included an AI co-author trailer, which the human rejected (above).
- The agent initially proposed fewer decision records than the human wanted.
- Four labelled eval cases abstain because the lexicon is thin, e.g. "never authorised" and "stopped
  working". The agent surfaced these rather than hiding them, and they are listed in `verify.md`.

## Human review notes
<!-- The submitting engineer should add their own review findings here before submitting: what they
     read line by line, what they changed, and anything they would do differently. This section is
     deliberately left for them to write in their own words. -->
