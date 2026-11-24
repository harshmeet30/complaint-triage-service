## What and why
<!-- What does this change do, and why? Link the ADR if it records a decision. -->

## Type of change
- [ ] Feature
- [ ] Fix
- [ ] Refactor / chore
- [ ] Docs / evidence only
- [ ] Classifier change (lexicon, thresholds or model)

## Verification
- [ ] `python scripts/verify.py` passes locally (lint, format, tests + coverage floor, eval gates)
- [ ] New or changed behaviour has tests, including the failure path
- [ ] Eval results attached below if the lexicon, thresholds or model changed

## Safety and privacy checklist
- [ ] No real customer, staff or confidential data added (synthetic only)
- [ ] No raw complaint text or PII added to logs, responses or storage
- [ ] No secrets or credentials committed
- [ ] Failure behaviour is stated (reject, abstain, or degrade) for any new input path

## Decisions
- [ ] New significant decision recorded as an ADR in `evidence/adr/` and listed in `evidence/decisions.md`
- [ ] Evidence pack updated if design, operation or known gaps changed

## AI assistance
- [ ] AI tool used: <!-- tool / model, or "none" -->
- [ ] I reviewed all generated code and take responsibility for it

## Merge notes
Use a merge commit or fast-forward. Do not squash or rewrite history.
