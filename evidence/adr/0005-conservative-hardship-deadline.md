# ADR-0005: Apply the 21-day clock whenever financial difficulty is indicated

- **Status:** Accepted · 2026-11-24

## Context
RG 271 sets 30 calendar days for standard complaints and 21 days for hardship and default-notice
complaints. A complaint can be abstained (no category) and still show financial difficulty.

## Decision
`hardship = category == financial_hardship OR "financial_difficulty" in vulnerability flags`. The shorter
deadline applies even if the category was abstained. Deadlines are calendar days from receipt.

## Alternatives considered
- Use the 21-day clock only on a confident hardship category: risks missing the shorter deadline.
- Business-day calculation: needs holiday calendars, out of scope.

## Consequences
+ Errs toward the stricter deadline, which a compliance reviewer can defend.
- Some complaints are held to 21 days when 30 would have been allowed.
- Interpretation of RG 271 should be confirmed with Compliance before production use.
