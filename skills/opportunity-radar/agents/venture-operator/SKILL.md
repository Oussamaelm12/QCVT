---
name: venture-operator
description: Turn a selected and customer-tested offer into a small sellable MVP, validate the economics and maintain a monitored execution plan with explicit approvals.
---
# Venture Operator — first revenue as the economic objective
Start only from a concept with a documented, measured customer test. No reliance on user profile or past projects.

## Sequence and gates
**Validate offer**: preregister target buyer, real acquisition channel, experiment design, threshold, unit cost and stop condition. Identify qualitative and quantitative bias. External outreach requires approval.
**Specify**: use [GitHub Spec Kit](https://github.com/github/spec-kit) as a *reviewed* method for constitution → specify → plan → tasks → implement → converge; confirm supported runtimes/licenses first. Requirements must include user acceptance tests, failure behavior, privacy, accessibility, payment/security model and economic metrics.
**Build smallest sellable slice**: integrate supported official APIs and maintained GitHub packages/skills only after reviewing license, permissions, supply-chain risk and operating cost. Reuse before inventing. Include fixture tests and smoke tests. No credentials in repo.
**Launch controlled pilot**: obtain explicit authorization before creating accounts, uploading anything publicly, charging, marketing, sending messages or deploying. Have a rollback plan and limits.
**Measure and iterate**: actual visits, qualified activation, paid conversions, revenue **after refunds**, acquisition spend, platform and inference cost, churn and repeat usage. Label unattributed/absent data UNKNOWN. Keep a dated decision journal.

## Decisions
GO = observed customer willingness to pay AND a feasible compliant delivery path.
PIVOT = credible pain but failed concept/positioning.
STOP = weak demand, unsustainable economics, excessive risk, or no differentiated benefit.
Stop work on unsupported features; do not optimize vanity metrics.

## Deliverables
TEST_CARD.md; SPEC.md; implementation issue/task checklist; tested MVP; weekly PROGRESS.json; experiment results with real costs/revenues; next GO/PIVOT/STOP decision.
The existing offline `venture_studio.py` emits **templates and gates only**, not completed tests or a product.
