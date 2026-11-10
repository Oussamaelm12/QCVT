#!/usr/bin/env python3
"""Read-only Apple iTunes Search API discovery; standard library only."""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = "https://itunes.apple.com/search"
MAX_BYTES = 2_000_000

def fetch(term, country="us", limit=25, opener=None):
    if not term.strip() or len(term) > 200:
        raise ValueError("term must contain 1..200 characters")
    if not 1 <= limit <= 50:
        raise ValueError("limit must be 1..50")
    if len(country) != 2 or not country.isalpha():
        raise ValueError("country must be ISO two-letter code")
    params = urllib.parse.urlencode({"term": term, "country": country.lower(), "media": "software", "entity": "software", "limit": limit})
    url = BASE + "?" + params
    request = urllib.request.Request(url, headers={"User-Agent": "OpportunityRadar/0.3 (read-only research)", "Accept": "application/json"})
    if opener is None:
        opener = urllib.request.urlopen
    with opener(request, timeout=12) as response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("response too large")
        payload = json.loads(raw)
    apps = []
    for app in payload.get("results", []):
        if app.get("wrapperType") != "software":
            continue
        apps.append({
            "app_id": app.get("trackId"), "name": app.get("trackName"),
            "publisher": app.get("artistName"), "url": app.get("trackViewUrl"),
            "rating": app.get("averageUserRating"), "rating_count": app.get("userRatingCount"),
            "price": app.get("price"), "currency": app.get("currency"),
            "genres": app.get("genres", []), "description": app.get("description", "")[:1200],
        })
    return {
        "query": term, "country": country.lower(), "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_url": url, "source": "Apple iTunes Search API",
        "disclaimer": "Search relevance is not market share; ratings and price are not downloads or revenue.",
        "apps": apps,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("term")
    parser.add_argument("--country", default="us")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = fetch(args.term, args.country, args.limit)
        output = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output + "\n")
        else:
            print(output)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
