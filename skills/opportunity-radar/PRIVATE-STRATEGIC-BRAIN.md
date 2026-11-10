# Private Strategic Business Brain — personal decision cockpit (v0)

**Purpose:** private decision support for arbitrating independent business opportunities and directing research, experimentation and execution. This is NOT a product for external customers.

## Strict separation of information
1. **Market attractiveness:** derived only from external market evidence and explicitly supplied ratings; never use user profile, prior projects, preferences or personal history. Reuses conservative `decision_engine.py`. Source URLs are NOT fact-checked automatically.
2. **Execution feasibility:** optional explicit budget, hours and test-cost estimates in a SEPARATE private file. This does not change the market ranking; it only displays fit/mismatch. No past user context is imported.
3. **Decision memory:** append-only JSONL record of user-confirmed decisions, rationale, supporting references and next review. It does not learn automatically or independently authenticate a GO.
4. **Strategic guidance:** human-reviewed evidence, objections, experiments and a measurable next action. Never represent estimates as observed profit.

## Run offline, locally, privately
Do not store live business opportunities, execution constraints or decision history in the PUBLIC QCVT repo. Copy the code to a verified private directory/repository and execute there.

Example `portfolio.json` (synthetic placeholders, not recommendations):
```json
{
  "businesses": [
    {
      "id": "opportunity_001",
      "market": {
        "title": "EXTERNALLY RESEARCHED OPPORTUNITY",
        "ratings": {},
        "evidence": []
      }
    }
  ]
}
```
Example optional `constraints.json`:
```json
{
  "budget_eur": 0,
  "hours_per_week": 0,
  "estimates": {
    "opportunity_001": {
      "estimated_test_cost_eur": null,
      "estimated_test_hours": null
    }
  }
}
```
```bash
python3 -m unittest discover -s skills/opportunity-radar/tests -v
python3 skills/opportunity-radar/scripts/strategic_brain.py arbitrate \\
  --portfolio /private/business-os/portfolio.json \\
  --constraints /private/business-os/constraints.json \\
  --output /private/business-os/decisions/arbitration-v1.json
```
Omit `--constraints` to avoid any personal execution data. Output files are exclusive-create (never overwritten).

Record a *user-confirmed* decision in `entry.json`:
```json
{
  "business_id":"opportunity_001",
  "decision":"RESEARCH",
  "reason":"Independent market evidence and customer commitment are missing",
  "evidence_refs":[],
  "next_review":"2026-11-17"
}
```
```bash
python3 skills/opportunity-radar/scripts/strategic_brain.py record-decision \\
  --journal /private/business-os/decisions/journal.jsonl \\
  --entry /private/business-os/entry.json
```

## What is implemented vs pending
**Implemented:** private-compatible offline decision data contract, deterministic market ranking independent of personal constraints, separate execution fit, append-only decision journal with per-record hash link, tests, read-only source research connectors and structured innovation dossiers.

**Not implemented:** private repo creation/migration, authenticated encrypted storage, UI cockpit, autonomous multi-agent strategy synthesis, verified market research, genuine self-learning from outcomes, monitoring, real commercial validation, external account actions or paid deployments.

## Next technical gates
- Confirm a **private** working location before persisting real ideas or private budgets.
- Connect source-verified Opportunity Radar records into the portfolio schema with deduplication and provenance.
- Build scenario/sensitivity analysis that never changes market facts; expose confidence, missingness and competing evidence.
- Add private searchable decision memory, actual experiment outcome logging and review cadence.
- Introduce a human-approved strategy model with red-team, citations and a measurable evaluation benchmark.
- Add a private cockpit only after these foundations pass integration/security tests.

**No spend, publication, repo visibility changes or deployment is authorized by this document.**
