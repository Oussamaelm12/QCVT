# Decision Engine v1 — conservative decision support

This is a private-use-oriented, read-only scoring component; **not** an automated proof of product-market fit.

## Input format
Create a local JSON file with `{"candidates":[{"title":"Example idea","ratings":{"pain":3,"demand":2,"distribution":4,"economics":3,"feasibility":5,"competition":2,"risk":3},"evidence":[{"kind":"review","url":"https://example.org/review","observed_at":"2026-11-10","claim":"A user reports a specific recurring problem"}]}]}`.
Scores are **human-supplied 0–5 assumptions**, not inferred or verified from web links. A URL is recorded for audit, not automatically checked for truth. A URL can be fictitious; the engine does not fetch or authenticate it. Do not enter sensitive private ideas into public GitHub files or workflow inputs.

## Run
`python skills/opportunity-radar/scripts/decision_engine.py --input /secure/local/candidates.json --output /secure/local/ranking.json`

## Scoring
Weights: pain 25, demand 20, distribution 20, economics 15, feasibility 10, competition 5, risk 5. Scores are capped at 35 for incomplete ratings or fewer than two source domains, 65 when no direct customer signal exists, 100 otherwise. Source domain count is only a proxy for independence; source duplication and syndicated content require manual review. Statuses: UNSUPPORTED, DISCOVERY, RESEARCH, TESTED_SIGNAL. Even TESTED_SIGNAL does not mean validated profitability.

## Future iterations
1. Independent claim verification and domain/source normalization.
2. Automatic candidate extraction from source records with evidence spans.
3. Date freshness and source credibility, independent corroboration and contradiction handling.
4. Calibrated rankings using retrospective experiments, not arbitrary assumptions.
5. Customer discovery, pricing tests and measurable conversion evidence.
6. Decision memory and feedback loop in a **private** repository or local encrypted storage.

## Privacy
Do not run with personal hypotheses on the currently public QCVT repository. The private dedicated repository must be provisioned and its visibility verified first.
