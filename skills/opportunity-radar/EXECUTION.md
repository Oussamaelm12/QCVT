# Opportunity Radar v0.4 — execution and reliability

## What is implemented
- `SKILL.md`: evidence-first research routing to third-party skills, without executing them
- `scripts/pipeline.py`: live read-only multi-query Apple iTunes Search API discovery, deduplicates app IDs, keeps per-query provenance and partial failures
- `scripts/itunes.py`: single-query metadata fetch
- `scripts/score.py`: offline weighted idea evaluation with separate evidence sufficiency gate
- `scripts/economics.py`: explicit subscription sensitivity scenario, not a prediction
- `tests/`: offline unit tests using fake responses, no network, no credentials
- GitHub Actions workflow: offline unit tests on pull requests

## Run a small, reproducible first scan
```bash
python3 skills/opportunity-radar/scripts/pipeline.py \
  --query "budget planner" \
  --query "expense tracker" \
  --query "spending tracker" \
  --country fr --limit 25 --output research/budget-planner-fr.json
```

Inspect `failed_queries`, `apps`, `matched_queries`, `source_urls`. App Store presence is **not** a demand/revenue estimate. The next human or approved skill should read recent reviews, collect at least two independent evidence sources, inspect pricing, and formulate a falsifiable test. Do not feed raw ratings into the idea score as market size.

```bash
python3 -m unittest discover -s skills/opportunity-radar/tests -v
python3 skills/opportunity-radar/scripts/score.py skills/opportunity-radar/examples/ideas.json
python3 skills/opportunity-radar/scripts/economics.py --price 20 --conversion 0.02
```

## Security and cost
All local Python scripts use the standard library only. The pipeline accesses the fixed `https://itunes.apple.com/search` endpoint and does not follow user-provided URLs. It caps responses at 2 MB, limits to ten queries, and spaces requests by at least 0.5s in the CLI. No paid services, API tokens, GitHub secrets, third-party skill execution, or automated deployment. GitHub Actions tests do not access live APIs.

## Known limitations
- Real Apple API reachability, Apple usage policies, localization and rate limits require an actual live run.
- No Reddit, Google Trends, Sensor Tower, SEO or user-review adapters have been connected yet.
- A single platform cannot prove a viable opportunity. Source availability and coverage are not guaranteed.
- The score is provisional and its evidence sufficiency gate is not proof of product-market fit.
- GitHub Actions may require repository settings/permissions; inspect checks after push.

## v0.5 — second independent source and evidence fusion

`scripts/hackernews.py` uses the public Hacker News Algolia API, read-only and without a token, to retrieve dated discussion links, titles, comments and points. These are discovery leads, **not verified user pain**.

`scripts/evidence.py` combines exported Apple and HN JSON files, deduplicates stable IDs, and preserves source URLs. It explicitly sets `validation_ready=false`: two source types alone do not validate a market.

```bash
python3 skills/opportunity-radar/scripts/hackernews.py "budget planner" --hits 30 --output research/hn-budget.json
python3 skills/opportunity-radar/scripts/pipeline.py --query "budget planner" --query "expense tracker" --country fr --output research/apps-budget.json
python3 skills/opportunity-radar/scripts/evidence.py research/apps-budget.json research/hn-budget.json --output research/budget-evidence.json
python3 -m unittest discover -s skills/opportunity-radar/tests -v
```

No live API requests or CI checks were run as part of this commit. GitHub workflow runs associated with the latest commit were not returned when checked. Inspect GitHub Actions status before relying on these modules. Human evidence review and real demand validation remain required.
