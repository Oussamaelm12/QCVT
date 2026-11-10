# Opportunity Radar — usable research MVP

A read-only, budget-conscious **research assistant**, not an autonomous profit generator. The system integrates Apple App Store search, Apple recent reviews, Hacker News public discussions, evidence inventory, weighted scoring, and scenario calculations. All scripts use Python's standard library.

## One command: discovery
```bash
python3 skills/opportunity-radar/scripts/discover.py \
  --query "budget planner" \
  --query "expense tracker" \
  --country fr --app-limit 20 --hn-limit 20 --reviews 2 \
  --output research/first-scan.json
```
This produces a JSON dossier with source links, raw snippets, API errors, counts, and an explicit warning that **no opportunity is yet validated**.

## Score a candidate
Create a JSON file with `ideas` as in `examples/ideas.json`, adding 3 distinct observed claims with HTTPS URLs, capture dates, geography, 2 source domains, a distribution channel and falsifiable experiment. Run:
```bash
python3 skills/opportunity-radar/scripts/score.py skills/opportunity-radar/examples/ideas.json
python3 skills/opportunity-radar/scripts/economics.py --price 20 --conversion 0.02
```
Scores are provisional. The evidence gate is a minimum research threshold, not a guarantee of market fit.

## Tests and live API check
```bash
python3 -m unittest discover -s skills/opportunity-radar/tests -v
```
GitHub Actions runs offline tests and a separate **non-blocking** public API smoke test on pull requests. Its artifact `opportunity-radar-live-smoke` contains the actual collected JSON when network requests succeed. If all sources fail, the live job fails but the offline tests remain informative. No paid API keys, installations, or publishing.

## Missing integrations
Google Trends/SerpApi, Reddit, paid app analytics, SEO keyword volumes and third-party skills are **not integrated**. They require provider credentials, approval and security review. It would be inaccurate to call this a complete all-internet skills agent. Do not claim validated market opportunities without examining actual evidence and monetization.

## Safety
Read-only fixed public API endpoints, input validation, bounded responses, no secrets in repo, no automatic third-party skill installation, no scheduled recurring requests, no costs beyond GitHub Actions quota and public endpoints subject to provider terms. Review the privacy implications of saving user-generated comments and avoid storing personal identifiers.

## v0.7 — optional Reddit and Google Trends connectors

Two adapters are now included in `scripts/integrations.py` and orchestrated by `scripts/enrich.py`:

- Reddit: official OAuth API, requiring `REDDIT_ACCESS_TOKEN` and a descriptive `REDDIT_USER_AGENT`. Neither is included or obtained automatically. Public posts are discovery leads only.
- Google Trends: SerpApi, requiring `SERPAPI_KEY` and **explicit** `--allow-paid-trends`. SerpApi can consume billable credits. The output includes relative interest indices, **not** keyword volume. Do not enable until the user approves a spending/credit cap.

Optional enrichment of a previously generated dossier:

```bash
# Only after connecting a compliant Reddit OAuth token
python3 skills/opportunity-radar/scripts/enrich.py research/first-scan.json \
  --reddit --output research/reddit.json

# Only after explicit approval for SerpApi credits
python3 skills/opportunity-radar/scripts/enrich.py research/first-scan.json \
  --trends --allow-paid-trends --output research/trends.json
```

**Important:** The above external connectors are implemented but not yet live-tested against authenticated provider accounts. External GitHub skill repositories listed in `SKILL.md` remain reviewed references, not installed executables. No claim of being the world's highest-performing agent is justified without independent benchmark comparisons, representative datasets, and repeatable metrics. For safe operation, credentials belong in a secret manager, not in source code or artifacts.

## Production use — release candidate

**Run locally (Python 3.12+; no dependencies):**
```bash
python3 skills/opportunity-radar/scripts/production.py \
  --query "budget planner" --country fr \
  --output-dir research/output
```
Outputs: `research/output/dossier.json` (structured provenance, errors and raw research leads) and `research/output/REPORT.md` (readable summary).

**Run from GitHub:** After the PR is approved and merged into the default branch, open Actions → **Opportunity Radar — run research** → Run workflow, enter a query and choose the country. Download the `opportunity-radar-production-report` artifact. Until merged, the PR workflow runs a fixed demonstration query and uploads a `opportunity-radar-production-smoke` artifact; it does **not** provide arbitrary-query one-click production runs.

**Release criteria:** CI offline tests green; public API smoke produces data with no errors; Markdown and JSON artifact exists; no credentials or spending required. This is a **research MVP**, not an autonomous market-validation or profit-forecasting system. Reddit and Trends remain optional credential-gated integrations, not part of the default production run. Do not merge or deploy without review.
