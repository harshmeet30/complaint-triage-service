# Design

## Data flow
```
POST /complaints
   │  pydantic validation (10-5000 chars, no NUL, date not in future)  ──► 422, nothing stored
   ▼
redact()            PII → [CARD] [PHONE] [EMAIL] [BSB] [ACCOUNT] [TFN]      (raw text ends here)
   ▼
classify()          lexicon scores → category + confidence, or ABSTAIN (reason)
detect_vulnerability()  independent flags: family violence, bereavement, health, elderly, financial difficulty
   ▼
service.triage()    priority + hardship + RG 271 due date
   ▼
Store.save()        SQLite, redacted text only  ──► StoreError → generic 503
   ▼
201 response · metadata-only log line · /review-queue if abstained
```

## Components and boundaries
| Module | Responsibility | Depends on |
|---|---|---|
| `redaction.py` | PII removal, Luhn check | nothing |
| `classifier.py` | Scoring, abstain, vulnerability flags | nothing |
| `deadlines.py` | RG 271 date arithmetic | nothing |
| `service.py` | Orchestration, priority rules (pure, no I/O) | the three above |
| `store.py` | Persistence, error wrapping | `service` types |
| `api.py` | HTTP, validation, logging, error mapping | all |
| `evaluate.py` | Offline accuracy and safety gates | `classifier` |

The domain modules are pure functions, which keeps them trivially testable. I/O lives only in `store.py`
and `api.py`. The classifier is the swap point for an LLM or trained model (ADR-0002).

## Security and privacy
- Raw PII never reaches the classifier, database, API response or logs, and a test checks all four
  (ADR-0003, ADR-0008).
- Errors are generic to clients; detail is logged server-side only (ADR-0009).
- Inputs are bounded, so work per request is bounded (ADR-0010).
- Parameterised SQL only. No secrets exist in the slice.
- **Gaps:** no authentication or authorisation (ADR-0014), names and addresses are not redacted, and no
  encryption at rest (SQLite file).

## Trade-offs
Explainability and offline operation over recall (ADR-0002). Safety over automation, in the form of an
abstain rate of about 20% (ADR-0004). Stricter deadlines over fewer false alarms (ADR-0005).

## Likely production / cloud shape
```
API gateway (OIDC, WAF) ─► triage service (container, autoscaled) ─► Postgres (encrypted, private subnet)
                                   │                                  ▲
                                   ├─► durable queue ─► review-queue worker / case-management system
                                   └─► structured logs + metrics ─► central observability, alerting
Secrets: cloud secret manager · Config: environment · Raw-text vault: separate, access-controlled, retention-limited
```
- **Auth:** OIDC through the enterprise IdP. Roles: handler, team lead, auditor. Reads are audited.
- **Classifier:** the lexicon is replaced or augmented by a model served behind the same interface, with
  the eval gates unchanged and the abstain policy still deciding what reaches a person.
- **Resilience:** a durable queue or outbox, so storage outages queue the work instead of failing it.
- **Delivery:** see the CI/CD path in `operate.md`.
