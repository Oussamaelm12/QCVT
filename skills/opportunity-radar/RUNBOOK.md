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

## V0.3 — live-source adapter and unit economics
The `scripts/itunes.py` adapter reads only Apple's public iTunes Search API over HTTPS. No API key required. Search metadata and app ratings are **not** evidence of downloads, revenue or willingness to pay. Actual availability/rate limits depend on Apple's service. Run:

```bash
python3 skills/opportunity-radar/scripts/itunes.py "habit tracker" --country us --limit 25 --output apps.json
python3 skills/opportunity-radar/scripts/economics.py --price 20 --conversion 0.02
python3 -m unittest discover -s skills/opportunity-radar/tests -v
```

The economics script gives a **scenario** rather than a prediction. Assumed conversion, fees and fixed costs are editable; taxes, churn, refunds, acquisition labor and omitted costs are excluded. The iTunes adapter is intentionally separate from scoring so unsupported market metrics cannot silently enter the rubric.

### Runtime status
The adapter's mocked-response unit tests have been run locally and passed; live Apple API access has **not** been verified. Tests in GitHub should be run again in the target runner. No external skills have been installed or executed.
