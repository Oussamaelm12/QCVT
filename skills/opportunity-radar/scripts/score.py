#!/usr/bin/env python3
"""Opportunity Radar: deterministic, offline scoring of evidence-backed ideas.
No network access, API keys, third-party dependencies, or external writes beyond --output.
Usage: python3 skills/opportunity-radar/scripts/score.py input.json --output report.json
"""
import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

WEIGHTS = {
    "pain": 20,
    "distribution": 20,
    "monetization": 15,
    "competition_gap": 15,
    "feasibility": 15,
    "retention": 10,
    "risk": 5,
}
VALID_TYPES = {"observed", "estimated", "hypothesis"}
MAX_AGE_DAYS = 365

def evaluate(idea):
    evidence = idea.get("evidence", [])
    accepted = []
    warnings = []
    domains = set()
    unique_observed = set()
    for i, item in enumerate(evidence):
        url = item.get("url", "")
        host = urlparse(url).hostname
        typ = item.get("type")
        captured = item.get("captured_at")
        if typ not in VALID_TYPES or not host or urlparse(url).scheme != "https" or not captured or not item.get("claim") or not item.get("geography"):
            warnings.append(f"evidence[{i}]: invalid type, URL or date")
            continue
        try:
            age = (date.today() - date.fromisoformat(captured)).days
            if age < 0:
                warnings.append(f"evidence[{i}]: future date")
                continue
            if age > MAX_AGE_DAYS:
                warnings.append(f"evidence[{i}]: older than one year; excluded")
                continue
        except ValueError:
            warnings.append(f"evidence[{i}]: invalid date")
            continue
        accepted.append(item)
        if typ == "observed":
            canonical = (url.split("#", 1)[0].rstrip("/"), item["claim"].strip().casefold())
            if canonical in unique_observed:
                warnings.append(f"evidence[{i}]: duplicate observation; excluded")
                accepted.pop()
                continue
            unique_observed.add(canonical)
            domains.add(host.lower().removeprefix("www."))
    scores = idea.get("scores", {})
    missing = [k for k in WEIGHTS if k not in scores]
    for k, value in scores.items():
        if k not in WEIGHTS or not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 5:
            raise ValueError(f"{idea.get('name','idea')}: invalid score {k}={value}")
    provisional = sum(scores.get(k, 0) * w / 5 for k, w in WEIGHTS.items())
    observed = sum(e.get("type") == "observed" for e in accepted)
    estimated = sum(e.get("type") == "estimated" for e in accepted)
    # Evidence sufficiency is a separate gate, not a fake probability of success.
    sufficient = observed >= 3 and len(domains) >= 2 and not missing
    if missing:
        warnings.append("missing score dimensions: " + ", ".join(missing))
    if observed < 3:
        warnings.append("fewer than three observed evidence records")
    if len(domains) < 2:
        warnings.append("fewer than two distinct observed-source domains")
    if not idea.get("distribution_channel"):
        warnings.append("missing organic distribution channel")
    if not idea.get("test"):
        warnings.append("missing falsifiable experiment")
    ready = sufficient and bool(idea.get("distribution_channel")) and bool(idea.get("test"))
    return {
        "name": idea.get("name", "Unnamed"),
        "score_out_of_100_provisional": round(provisional, 1),
        "evidence_ready": ready,
        "observed_count": observed,
        "estimated_count": estimated,
        "distinct_observed_domains": len(domains),
        "warnings": warnings,
        "recommendation": "INVESTIGATE" if ready else "INSUFFICIENT EVIDENCE",
        "next_test": idea.get("test"),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    results = [evaluate(i) for i in payload.get("ideas", [])]
    results.sort(key=lambda x: (x["evidence_ready"], x["score_out_of_100_provisional"]), reverse=True)
    report = {
        "generated_on": date.today().isoformat(),
        "status": "OFFLINE EVIDENCE SCORING — not a live market research run",
        "weighting": WEIGHTS,
        "results": results,
    }
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

if __name__ == "__main__":
    main()
