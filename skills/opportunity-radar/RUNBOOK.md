# First executable slice

This is an **offline, standard-library-only evidence scorer**, not a market crawler. It accepts manually verified evidence collected using the source skills listed in SKILL.md. It does not install or execute third-party skills.

## Run
```bash
python3 skills/opportunity-radar/scripts/score.py skills/opportunity-radar/examples/ideas.json
python3 -m unittest discover -s skills/opportunity-radar/tests -v
```

## Evidence format
Each idea needs `name`, `distribution_channel`, `scores` (seven dimensions, 0–5), `evidence` array and a `test` with a falsifiable success metric. Each evidence item needs `url`, `captured_at` (YYYY-MM-DD), `type` (observed/estimated/hypothesis), `claim`, `geography`. A score is provisional unless three observed records from two independent domains exist and all dimensions are scored.

## Next implementation milestone
Build separately permissioned source adapters: official iTunes Search/RSS first; Google Trends via user-approved API key second; Reddit only with valid API access third. Add provenance hashes, caching, source-specific reliability and tests before allowing any auto-ranking to drive a build decision.

## Security
Review external skill code and transitive dependencies before execution. Do not expose tokens in logs or commit credentials. No spending, publishing or scraping behind access controls without explicit approval.
