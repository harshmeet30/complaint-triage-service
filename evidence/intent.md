# Intent

## Problem
Retail banks receive a high volume of free-text customer complaints across channels. Under ASIC
Regulatory Guide 271 (Internal Dispute Resolution), each complaint must be recorded, acknowledged
and resolved within set timeframes: **30 calendar days** for standard complaints and **21 days** for
complaints about financial hardship or default notices. Triage is often manual, which means:

- scam/fraud and hardship complaints (the time-critical, high-harm ones) wait in a general queue;
- the free text carries PII (card numbers, account numbers, phone numbers, emails) into downstream
  systems and logs;
- triage decisions aren't recorded consistently, which makes them hard to audit.

## Solution (thin vertical slice)
A locally runnable **complaint triage service** that takes one synthetic complaint and:

1. validates the input, rejecting malformed or oversized submissions;
2. **redacts PII** before anything is stored or logged;
3. **classifies** the complaint into a category, scores its confidence and flags vulnerability indicators;
4. assigns priority and the **RG 271 response deadline**;
5. **abstains** (routes to the human review queue) when confidence is low or the signals are ambiguous;
6. stores the redacted record with an audit trail of *why* the decision was made.

## Intended users
- **Complaints-handling officers**: get a prioritised queue with deadlines.
- **Complaints/IDR team leads**: review the abstain queue.
- **Risk and compliance**: audit why each complaint was routed the way it was.

## Assumptions
- Input comes in as text through an API (channel integration is out of scope).
- Complaints are in English.
- The deadline is counted from the received date in calendar days, as RG 271 specifies. Business-day and
  public-holiday calendars are out of scope.
- A deterministic, explainable classifier is acceptable for the first slice. An LLM classifier can be added
  later behind the same interface (see `decisions.md`).

## Constraints
- 3-hour build timebox.
- Runs offline. No paid APIs, credentials or containers needed for the core path.
- Synthetic data only. No real customer data.

## Out of scope
- Authentication/authorisation (described for production in `design.md`, not built).
- Channel ingestion (email, call-centre transcripts), attachments, non-English text.
- Case management workflow beyond triage (assignment, resolution, AFCA escalation).
- Named-entity PII such as personal names and addresses (a known gap, see `verify.md`).

## Success criteria
| # | Criterion | How it's checked |
|---|-----------|------------------|
| S1 | One complaint goes from API request to persisted, triaged record end to end | API integration test plus the demo script |
| S2 | No raw PII is stored or logged for the supported patterns | Unit tests and a DB/log leak test |
| S3 | Invalid input is rejected with a clear 4xx and no side effects | Validation tests |
| S4 | Low-confidence or ambiguous complaints abstain to human review instead of guessing | Abstain tests plus the eval harness |
| S5 | Category accuracy ≥ 85% on the labelled synthetic eval set when the model doesn't abstain, with abstain rate ≤ 25% | Eval gate in `verify` |
| S6 | Hardship complaints get the 21-day deadline and everything else gets 30 days | Unit tests |
| S7 | A single command runs lint, tests and eval, as CI would | `verify` script |
