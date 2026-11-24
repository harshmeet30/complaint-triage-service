# ADR-0004: Abstain to human review on weak or ambiguous signals

- **Status:** Accepted · 2026-11-24

## Context
A wrong confident category on a scam or hardship complaint is worse than a slower human decision.

## Decision
Abstain (status `needs_review`, no category) when any of these holds:
- no lexicon match (`no_signal`);
- top score below 2 (`weak_signal`);
- confidence below 0.6 (`ambiguous_categories`).

Abstained complaints go to `/review-queue`, ordered by due date. The abstain reason is stored.

## Alternatives considered
- Always pick the top category: higher automation, but silent misrouting.
- Lower threshold (0.5): fewer abstains, with more risk on mixed complaints.

## Consequences
+ Mixed-signal complaints (e.g. "can't afford repayments because I was scammed") reach a person.
- Humans carry the load of ~20% abstains on the eval set. The threshold is a policy lever, to be tuned
  against real reviewer capacity and error cost.
