# Agentic workflow

## Tools
- **Claude Code** (CLI) was the primary implementation tool. It wrote the code, tests and documentation
  and ran the commands. I directed the work, set the quality bar, and reviewed every phase before the next.
- Models: Claude Opus 5.5 for the early phases, then Claude Sonnet 5.5 from phase 2 onwards.
- No other AI tools. No hosted model APIs in the product. No private data.

## Approach: spec first, small phases, gates before features
1. Wrote the problem, constraints and **measurable success criteria first** (`intent.md`, S1-S7), so every
   phase had a testable target.
2. Built in phases with a human checkpoint after each, committing small steps to `dev`.
3. Put the **verification gate in place before building the service layer**, then tightened it as the
   code grew.
4. Recorded every significant decision as an **ADR** as it was made.

| Phase | Output | Commit(s) |
|---|---|---|
| 1. Frame | `intent.md`, success criteria, scaffold | `7ccea90` |
| 2. Core engine | PII redaction, classifier with abstain, RG 271 deadlines, unit tests | `de49666`, `6c8ad15` |
| 3. CI gate | `scripts/verify.py` and GitHub Actions, before the service layer | `1406176` |
| 4. Service | validation, SQLite store, FastAPI, 503 path, PII-leak test | `8cfdb7f` |
| 5. Eval | labelled set, harness with four gates, wired into the gate | `26db441` |
| 6. ADRs | 15 decision records and an index | `d76ade7` |
| 7. Docs | README with flow diagrams, demo, design, verify, operate | `5b34df0` |
| 8. Quality gates | coverage floor, format check, PR template, ADR-0016 | `6cdff3d` |

## Engineering interventions
Controls I put on the agent's work, and why.

| Intervention | Why | Where |
|---|---|---|
| Chose the problem (complaint triage) from the options proposed | Maps to real obligations: RG 271 timeframes, privacy, vulnerable customers | ADR-0001 |
| Required `dev` to `main` branching with no squash | Preserve the incremental history the brief asks for | ADR-0013 |
| **Added a CI gate before further build** | Every later phase is verified from the start, not retrofitted | `1406176`, ADR-0012 |
| **Required an ADR for every decision**, not just 3-5 | Decisions stay traceable and defensible in review | ADR-0001 to 0016 |
| **Required lint, format, unit tests, coverage floor and a PR template in CI** | Quality enforced by the pipeline, not by memory | `6cdff3d`, ADR-0016 |
| Required architecture and flow diagrams in the README | A reviewer can understand the slice in a minute | `5b34df0` |
| Set the attribution policy: no AI co-author trailers in commits, AI use disclosed in the README and here | Disclosure is explicit and in one auditable place | ADR-0013 |
| Kept the repo free of employer names and any real data | Public repo, synthetic data only | ADR-0015 |

## Representative steering instructions
These are the instructions I gave the agent at each control point, written out in full. They are
representative: the live session used shorter messages carrying the same requirements, and no verbatim
transcript is claimed. Each states context, requirements and an acceptance check.

**1. Framing (phase 1).**
> Build a complaint-triage service for a regulated bank, runnable offline with no paid keys. Before any
> code, write `evidence/intent.md`: problem, users, assumptions, out-of-scope, and numbered success
> criteria that can each be checked by a named test or command. Cover ASIC RG 271 timeframes (30 days,
> 21 for hardship). Acceptance: every criterion maps to a test; nothing real or confidential is used.

**2. Privacy boundary (phase 2).**
> Redact PII before anything is classified, stored or logged, so raw text never leaves the redactor.
> Cover cards (Luhn-checked to avoid destroying reference numbers), BSB, account numbers, AU phones,
> emails and TFNs. Acceptance: unit tests per pattern plus a false-positive test; state what is *not*
> covered (names, addresses) as a known gap rather than implying completeness.

**3. Safe-failure design (phase 2).**
> The classifier must abstain to a human rather than guess. Use margin-based confidence with explicit
> abstain reasons (no signal, weak signal, ambiguous), record the matched terms that drove each decision,
> and detect vulnerability indicators (family violence, bereavement, health, age, financial difficulty)
> independently so they still apply when the category is abstained. Acceptance: tests for each abstain
> reason, and an abstained vulnerable complaint is high priority.

**4. Gate before features (before phase 4).**
> Before building the service layer, add a single `scripts/verify.py` that runs the checks, and a GitHub
> Actions workflow that runs that exact command on push and pull request. Acceptance: one command passes
> locally and in CI; later phases extend the same command instead of adding separate steps.

**5. Service with guarded failure paths (phase 4).**
> Build the FastAPI service over a SQLite store: validate input (length, NUL characters, future dates)
> and reject with 422 and no side effects; fail closed with a generic 503 if storage fails, logging the
> detail server-side only; log metadata, never complaint text. Acceptance: a test that submits real-looking
> PII and asserts none of it appears in the response, the database dump or the captured logs; a test for
> each rejection and for the 503 path.

**6. Measured quality (phase 5).**
> Create a labelled synthetic eval set including deliberately ambiguous cases, and an eval harness with
> CI gates: accuracy on answered cases, abstain rate, recall on cases that should abstain, and zero
> scam or hardship complaints confidently put in the wrong category. Acceptance: tests that feed the
> harness bad data and confirm it fails. State plainly that the lexicon and eval set share an author, so
> the score is optimistic.

**7. Decision records.**
> Write one short ADR for every significant decision, not only three to five: context, decision,
> alternatives, consequences, plus an index. Include the deliberate gaps (no authentication) and the
> eval bias. Acceptance: each decision visible in the code or tests has an ADR, and new decisions get
> the next number.

**8. Pipeline quality.**
> Strengthen the gate: add a format check, branch coverage with a 95% floor, and a pull-request template
> covering verification, privacy, ADRs and AI assistance. Close coverage gaps with tests, not exclusions
> or `pragma: no cover`. Acceptance: coverage reported per file, the floor enforced in CI, and the
> template present.

**9. Documentation for a reviewer.**
> README with a request-flow diagram, a component diagram and the delivery path, plus setup, run, verify,
> a worked example and known limitations. Acceptance: someone can clone, install and run the demo from
> the README alone, and every limitation is stated.

## How output was verified
- **Single command:** `python scripts/verify.py` runs lint, format check, tests with a 95% branch-coverage
  floor, and the eval gates. Local and CI run the same command.
- **Risk-weighted tests:** PII leakage is checked across the API response, the database and the logs
  together. Each failure path (422 rejection, 503 storage failure, abstain) has its own test.
- **Gates that can fail:** the eval harness is tested with deliberately wrong data to confirm it fails,
  so it can't pass vacuously.
- **Run for real:** the live server was started and called over HTTP, and the demo script output is what
  the README shows.
- **Honest limits recorded:** the eval set shares an author with the lexicon, so its accuracy is
  optimistic (ADR-0011, `verify.md`).

## Review findings
What the review gates caught, and what changed as a result.
- **Coverage measured 87%.** Gaps were the store error paths, priority branches and the eval CLI. Closed
  with 14 tests, not exclusions: 99.5%.
- **Format check failed on 5 files.** Reformatted, and the check now blocks it.
- **Four labelled eval cases abstain** because the lexicon is thin (e.g. "never authorised"). They are a
  safe failure, and are listed in `verify.md` as the lexicon's known gaps.
- **Redaction does not cover names or addresses.** Documented as a known gap with the production fix.

## Human review notes
- Probed the redactor with formats beyond the agent's tests (spaced and dashed cards, +61 phones). Found names and addresses are not covered. Documented as a known gap rather than overclaiming.
- Reviewed the confidence formula and the 0.6 threshold. I accepted it as a policy lever, not a proven value. It would be tuned against reviewer capacity and error cost.
- Confirmed by reading the code that logs carry metadata only and storage errors return a generic 503. The PII-leak test checks response, DB and logs together.
- Challenged the 21-day rule for abstained financial-difficulty cases. I kept the conservative reading and flagged it for Compliance confirmation (ADR-0005).
- What I'd do with more time: an independent held-out eval set, NER for names and addresses, authentication, a durable queue, and Postgres with migrations.
- I'm accountable for all submitted code, including what the agent generated.