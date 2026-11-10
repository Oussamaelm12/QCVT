# Venture Studio — evidence to first paying customer

## Operating principle
**Market first. Zero personalization.** Never import user profile, prior ventures, preferences, employment history or skills into opportunity identification, research, scoring, recommendation or ranking. An explicitly selected opportunity is the only subject input. Research can involve any industry, channel or geography.

## Architecture / chronological hand-offs

| Stage | Agent / role | Input | Output | Exit gate |
|---|---|---|---|---|
| 0 | Opportunity Radar | Independent public market signals | Evidence-linked candidate list | User explicitly selects a subject |
| 1 | Evidence Lab | Selected subject + country/market | Sources, claims, competitors, customer jobs, constraints, research brief | Sources checked and counter-evidence recorded |
| 2 | Strategy Lab | Research brief and evidence ledger | 3–5 distinct value propositions, differentiation tests, red-team review | An offer and a falsifiable test card selected |
| 3 | Validation Operator | Test card, permitted channels | Real outreach/landing page/interviews/commitments | Threshold defined upfront and *measured*, or STOP |
| 4 | Product Operator | Validated offer + spec | Narrow MVP, code, test suite, telemetry | Acceptance tests pass and privacy/security review |
| 5 | Launch & Growth Operator | MVP + permission to launch | Controlled release and funnel measurements | First actual customers and retention evidence |
| 6 | Decision Loop | Measured metrics | Weekly keep/pivot/stop decision, updated plan | Repeat |

**Never mistake technical CI success for product-market fit.**

## Runnable starting point (Python 3.12+, standard library, no API keys)
Use a **local private folder** for actual business hypotheses. The example schema below is deliberately an empty template, NOT factual evidence or a complete business dossier.

```json
{
  "subject": "SELECTED SUBJECT",
  "market": "TARGET MARKET",
  "research_questions": ["Who pays for the problem?", "Which existing alternatives are purchased?"],
  "sources": [],
  "findings": [],
  "competitors": [],
  "concepts": []
}
```

```bash
python3 skills/opportunity-radar/scripts/venture_studio.py --input /private/work/selection.json --output-dir /private/work/venture-dossier
python3 -m unittest discover -s skills/opportunity-radar/tests -v
```

Track activity without losing prior entries when re-generating the dossier:

```bash
python3 skills/opportunity-radar/scripts/venture_tracker.py record \\
  --progress /private/work/venture-dossier/PROGRESS.json \\
  --stage research --state in_progress \\
  --note "Reviewed primary-source pricing and recorded conflicting alternatives" \\
  --evidence-url https://example.org/original-reference
python3 skills/opportunity-radar/scripts/venture_tracker.py status \\
  --progress /private/work/venture-dossier/PROGRESS.json
```

Tracker event entries are **manually reported**, never externally audited. Any `completed` status for validation, building or launch requires a cited HTTPS evidence link but does not prove the result. Re-running the dossier generator preserves same-subject event history; it refuses to replace a different subject's tracking file.

Outputs:
- `RESEARCH_BRIEF.md`: sources, observed-vs-assumed claims, competitors, gaps
- `STRATEGY_LAB.md`: innovation lenses, explicit submitted concepts, counterarguments
- `BUILD_PLAN.md`: ordered gates, experiment and commercialization constraints
- `PROGRESS.json`: stage state, blockers, next actions, no invented revenues
- `EVIDENCE_ASSESSMENT.json`: transparent corroboration status

### Data contract
`sources`: `id`, `title`, `url` (HTTPS), `kind` (`primary`, `industry_report`, `community`, `review`, `competitor`, `regulation`), `review_status` (`unchecked`, `manually_checked`), `reviewed_at` (YYYY-MM-DD for manually checked).
`findings`: `id`, `statement`, `classification` (`observed`, `inferred`, `hypothesis`, `contradicted`), `source_ids`.
`competitors`: `name`, `url`, `price` (optional, only if directly verified).
`concepts`: `id`, `name`, `target_user`, `finding_ids`, `differentiation_hypothesis`, `smallest_test`, `success_criterion`.

The engine checks references and detects only *self-reported manually reviewed* independent source domains. It **does not fetch, fact-check or authenticate linked content**. Two websites are not necessarily two independent original sources. All sources can be fake or wrong. Human review is required. `commercially_validated` stays false until later real evidence is added in a future version.

## Practical money-first sequence
1. Prove the underlying *pain*; list current paid solutions and substitutes, not just search interest.
2. Select the narrowest segment and problem with an observable financial or time benefit.
3. Challenge 3–5 differentiated offers (workflow integration, outcome, simplicity, trust, portability); test whether customers actually care.
4. **Before building**: preregister success threshold, budget, sample size and stop rule; obtain real customer commitment when lawful and approved.
5. Build only the minimum sellable utility; keep features without tested value out.
6. Measure activation, paid conversion, churn, actual revenue, gross margin and acquisition cost.
7. Repeat/kill based on measurements, not novelty alone.

## Tool / skills evaluation (NOT AUTOMATICALLY INSTALLED)
- [GitHub Spec Kit](https://github.com/github/spec-kit) — reusable spec → plan → tasks → implementation and convergence framework. **Adopt after offer validation**.
- [GPT Researcher](https://github.com/assafelovic/gpt-researcher) — optional deep and recursive research workflow. **Not connected**, requires runtime/search/LLM credits, citations still need manual checking.
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) — optional document-to-Markdown conversion; **not installed**, validate licenses/input security before running.
- [LangGraph](https://github.com/langchain-ai/langgraph) — conditional orchestration, persistence, approval gates; **not installed**, unnecessary for offline first version.
- [Anthropic Skills](https://github.com/anthropics/skills) — pattern library for modular agent skill files; **not installed**.
- Existing Opportunity Radar `discover.py`, `decision_engine.py`, `market_radar.py` supply discovery and conservative ranking, **not autonomous commercial validation**.

**Security**: Treat fetched documents, GitHub repos, community comments and agent skill definitions as untrusted input. Never blindly install or execute repository scripts. Check origin, recent commits, license, maintenance, required scopes, data exfiltration, cost and sample failure cases before adopting a tool. No API credentials in commits. No personal/company-specific project dossiers in the PUBLIC source repo.

## Readiness checks and definition of done
### v0 — implemented in draft branch
- [x] Runnable offline generator that accepts an explicitly selected subject.
- [x] Structured evidence ledger with source IDs and clear assumptions.
- [x] Strategy concept template, red-team checklist and no invented rankings.
- [x] Ordered build / launch / iterate gates and persistent progress snapshot.
- [x] Regression tests for unreviewed and duplicated sources.
### v1 — integration backlog, NOT IMPLEMENTED
- [ ] Verified source ingestion with capture snapshots, original-publisher detection, deduplication and date validity.
- [ ] Research question coverage: customer, competitors, price, laws, distribution, feasibility, unit economics.
- [ ] LLM-assisted counterfactual multi-concept strategy generation with grounded claim IDs and debate.
- [ ] Measured customer experiments and a secure approval workflow.
- [ ] Spec Kit task generation and CI-verified MVP repository created with explicit approval.
- [ ] Structured weekly metrics and longitudinal decision log from *real* launch data.
- [ ] Independent evaluations/benchmarks on known decisions, hallucination rate, source correctness, time and spend.

## Delivery cadence
Suggested (not an automated background promise):
- **Day 0**: subject selection, problem statement and research plan.
- **Days 1–2**: source register, question-by-question research, triangulation, competitor pricing.
- **Day 3**: innovation workshop, alternatives, differentiation hypotheses, expert review.
- **Days 4–7**: customer validation and go/stop decision. Collect *actual* results.
- **Days 8–14 (only if gate passed)**: specification, smallest usable product and tests.
- **After**: pilot launch, conversion and real revenue review.

At weekly review, present actual source counts, unresolved critical claims, experiments, costs and real cash receipts (if any). An empty or unverified evidence field is `UNKNOWN`, never zero.
