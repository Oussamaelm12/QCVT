#!/usr/bin/env python3
"""Read-only Hacker News Algolia search for public discussion evidence.
Stdlib-only. Never equate mentions or votes with paying demand.
"""
import argparse
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://hn.algolia.com/api/v1/search_by_date"
MAX_BYTES = 2_000_000

def fetch(query, hits=30, opener=None):
    if not isinstance(query, str) or not 2 <= len(query.strip()) <= 120:
        raise ValueError("query must contain 2..120 characters")
    if not isinstance(hits, int) or isinstance(hits, bool) or not 1 <= hits <= 100:
        raise ValueError("hits must be 1..100")
    params = urllib.parse.urlencode({"query": query, "tags": "story", "hitsPerPage": hits})
    url = ENDPOINT + "?" + params
    request = urllib.request.Request(url, headers={"User-Agent":"OpportunityRadar/0.5 (research; read-only)","Accept":"application/json"})
    with (opener or urllib.request.urlopen)(request, timeout=15) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("response too large")
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("hits"), list):
        raise ValueError("unexpected response")
    results = []
    for hit in data["hits"]:
        if not isinstance(hit, dict):
            continue
        oid = str(hit.get("objectID") or "")
        if not re.fullmatch(r"\d+", oid):
            continue
        results.append({
            "id": oid,
            "title": str(hit.get("title") or "")[:300],
            "discussion_url": "https://news.ycombinator.com/item?id=" + oid,
            "external_url": hit.get("url"),
            "created_at": hit.get("created_at"),
            "points": hit.get("points"),
            "comments": hit.get("num_comments"),
        })
    return {
        "source": "Hacker News via Algolia public API",
        "source_url": url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "results": results,
        "disclaimer": "Discussion mentions are not evidence of market size, purchasing intent, or revenue. Read context before classifying pain."
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--hits",type=int,default=30)
    p.add_argument("--output",type=Path,required=True)
    args = p.parse_args()
    result = fetch(args.query,args.hits)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(args.output),"results":len(result["results"])}))

if __name__ == "__main__":
    main()
