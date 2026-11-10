# Venture Studio — implementation board (2026-11-10)

**Scope:** reusable evidence-first venture pipeline; NO user profile or prior project relevance. This is a development board, not market proof or a scheduled execution receipt. Source is a PUBLIC draft branch; no confidential selected-topic data belongs here.

## Current delivery — actually implemented
| ID | Component | Status | Evidence / acceptance |
|---|---|---|---|
| VS-00 | Radar intake contract and neutral operating skill | DONE (draft) | `SKILL.md` excludes profile and project-based targeting |
| VS-01 | Evidence-gated offline dossier | DONE (draft) | `scripts/venture_studio.py`, `RESEARCH_BRIEF.md` output |
| VS-02 | Strategy differentiation and red-team prompts | DONE as **skill specification**, not autonomous model | `agents/strategy-lab/SKILL.md`, `STRATEGY_LAB.md` |
| VS-03 | Chronological development plan | DONE (draft) | `BUILD_PLAN.md`, eight named phases |
| VS-04 | Durable progress and stage events | DONE (draft) | `scripts/venture_tracker.py`, `PROGRESS.json`; regenerated dossier retains entries |
| VS-05 | Technical regression checks | DONE (draft) | GitHub Actions offline tests; report most recent result separately |
| VS-06 | Proprietary storage | BLOCKED | Require a VERIFIED private repository or private local directory |

## Priority backlog: build in this order
| Priority | ID | Deliverable | Definition of done | Gate |
|---|---|---|---|---|
| P0 | VS-10 | Private isolated workspace | Confirm repository private; no public business notes, secrets or sensitive uploads | Explicit permission for repo creation/migration |
| P0 | VS-11 | Evidence ingestion adapter v1 | At least 2 allowed public APIs, request budgets, retries, dedup, precise URLs, capture timestamp, original-publisher metadata, failure log | Source access lawful and free, or approved cap |
| P0 | VS-12 | Evidence validation and contradiction engine | Extract claim spans; flag correlated sources and conflicts; benchmark with 20 annotated factual cases, no invented citations | Read-only |
| P0 | VS-13 | Deep Research agent v1 | For a **selected** topic, user questions and sources become a verifiable dossier with missing-data audit; run reproducibly | Private workspace |
| P1 | VS-14 | Strategy multi-concept engine | At least 3 structurally different product hypotheses; each linked to observed pain, red-team critique, build-vs-reuse option, measurable customer test | Research gate |
| P1 | VS-15 | Reusable skill and GitHub library registry | Origin, license, maintenance, security and API cost for each proposed dependency; no auto-install | Human review |
| P1 | VS-16 | Customer experiment card | Target, offer, price hypothesis, acquisition channel, test, observed response, predeclared threshold, actual cost and decision | Approval before outreach/payment |
| P1 | VS-17 | Spec-to-build pipeline | Reviewed Spec Kit-like spec, tasks, tests and smallest viable vertical slice; code PR, CI, rollback | Observed validation + approval |
| P2 | VS-18 | Pilot analytics and economics | Event-based acquisition funnel, paid receipts vs estimates, refund/churn/cost bridge | Approved launch |
| P2 | VS-19 | Weekly decision report | Source validity delta, actions done/blocked, verified metrics, GO/PIVOT/STOP and next experiment | Real data exists |

## Critical path
VS-10 → VS-11/12 → VS-13 → VS-14/15 → VS-16 → VS-17 → VS-18 → VS-19.
Skip VS-17 if the buying test fails. No backlog task automatically authorizes a real-world operation.

## Definition of the first value delivery
The earliest economically meaningful deliverable is **not** an attractive AI feature list: it is one directly observed customer problem, an offer demonstrably different from alternatives, and a repeatable, permissioned test that obtains a measurable purchase commitment. Only then authorize MVP spend.

## Follow-up protocol
- After a **subject is explicitly selected**, create one private project input and run Venture Studio.
- Update progress after every evidence review or experiment using `venture_tracker.py record`.
- On each weekly review, show DONE/BLOCKED, tests, findings, links to originals, source errors, actual commitments/revenue/costs (if any), and the next shortest action. Never mark forecast as revenue.
- Existing recurring Sunday market report is **discovery only**; the venture-specific follow-up is a separate track when a real topic exists.

## Current limitations
No automated deep web research, LLM-driven idea synthesis, customer outreach, real billing, deployment, production metrics or continuous GitHub issue sync is integrated yet. All external frameworks are evaluated references, NOT installed tools.
