#!/usr/bin/env python3
"""Enrich an existing Opportunity Radar dossier with opt-in external sources.
Requires explicit flags; never calls SerpApi without --allow-paid-trends.
"""
import argparse
import json
from pathlib import Path
from integrations import google_trends, reddit_search

def enrich(dossier, *, reddit=False, trends=False, allow_paid=False,
           reddit_fn=reddit_search, trends_fn=google_trends):
    if trends and not allow_paid:
        raise PermissionError("Trends requires --allow-paid-trends and approved API credits")
    queries=dossier.get("queries",[])
    if not isinstance(queries,list) or not 1<=len(queries)<=5:
        raise ValueError("dossier must contain 1–5 queries")
    output={"status":"ENRICHMENT, NOT VALIDATION","queries":queries,
            "source_results":[],"errors":[],"validated_opportunities":0}
    for query in queries:
        if reddit:
            try:
                output["source_results"].append(reddit_fn(query))
            except (OSError,RuntimeError,ValueError,KeyError) as exc:
                output["errors"].append({"source":"Reddit","query":query,"type":type(exc).__name__,"message":str(exc)[:200]})
        if trends:
            try:
                output["source_results"].append(trends_fn(query,geography=dossier.get("country","fr"),allow_paid=True))
            except (OSError,RuntimeError,ValueError,KeyError) as exc:
                output["errors"].append({"source":"Google Trends","query":query,"type":type(exc).__name__,"message":str(exc)[:200]})
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("dossier",type=Path)
    p.add_argument("--reddit",action="store_true")
    p.add_argument("--trends",action="store_true")
    p.add_argument("--allow-paid-trends",action="store_true")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if not a.reddit and not a.trends:p.error("choose --reddit and/or --trends")
    result=enrich(json.loads(a.dossier.read_text(encoding="utf-8")),reddit=a.reddit,trends=a.trends,allow_paid=a.allow_paid_trends)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"sources":len(result["source_results"]),"errors":len(result["errors"]),"output":str(a.output)}))
if __name__=="__main__":main()
