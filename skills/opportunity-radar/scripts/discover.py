#!/usr/bin/env python3
"""Single-command, read-only market discovery, with honest partial-failure reporting."""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from pipeline import research as app_research
from hackernews import fetch as hn_fetch
from evidence import merge as evidence_merge
from reviews import fetch_reviews

def run(queries, country="fr", app_limit=20, hn_limit=20, review_limit=2,
        app_fn=app_research, hn_fn=hn_fetch, review_fn=fetch_reviews, pause=1.0):
    if not 1 <= len(queries) <= 5 or any(not 2 <= len(q.strip()) <= 100 for q in queries):
        raise ValueError("provide 1–5 queries of 2–100 characters")
    if not re.fullmatch(r"[a-zA-Z]{2}", country):
        raise ValueError("invalid country")
    if not 0 <= review_limit <= 5:
        raise ValueError("review_limit must be 0..5")
    errors = []
    documents = []
    try:
        apps = app_fn(queries,country=country,limit=app_limit,pause=pause)
        apps["source"] = "Apple iTunes Search API"
        documents.append(apps)
        errors.extend({"source":"Apple","query":e.get("query"),"error":e.get("detail")} for e in apps.get("failed_queries",[]))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        apps = {"apps":[]}
        errors.append({"source":"Apple","error":str(exc)[:200]})
    hn_docs=[]
    for q in queries:
        try:
            d=hn_fn(q,hits=hn_limit)
            hn_docs.append(d)
            documents.append(d)
        except (ValueError,OSError,json.JSONDecodeError) as exc:
            errors.append({"source":"Hacker News","query":q,"error":str(exc)[:200]})
        if pause:
            time.sleep(pause)
    reviews=[]
    for app in apps.get("apps",[])[:review_limit]:
        app_id=app.get("id")
        if not isinstance(app_id,int):
            continue
        try:
            reviews.append(review_fn(app_id,country=country))
        except (ValueError,OSError,json.JSONDecodeError) as exc:
            errors.append({"source":"Apple reviews","app_id":app_id,"error":str(exc)[:200]})
        if pause:
            time.sleep(pause)
    inventory=evidence_merge(documents)
    review_count=sum(len(r.get("reviews",[])) for r in reviews)
    return {
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "status":"DISCOVERY COMPLETED; NOT BUSINESS VALIDATION",
        "queries":queries,"country":country.lower(),
        "app_count":len(apps.get("apps",[])),
        "hn_discussions":sum(len(d.get("results",[])) for d in hn_docs),
        "review_count":review_count,
        "inventory":inventory,
        "app_results":apps.get("apps",[]),
        "discussion_results":[r for d in hn_docs for r in d.get("results",[])],
        "review_results":reviews,
        "errors":errors,
        "warnings":[
            "App Store search rank and HN discussions are not evidence of paid demand.",
            "Ratings and reviews are self-selected; do not infer downloads or revenue.",
            "No verified pricing, search volume, willingness to pay or SEO competition has been established.",
            "The research is a discovery dossier, not an investment recommendation."
        ],
        "validated_opportunities":0,
        "next_action":"Manually verify recurring complaints across independent sources, pricing and organic distribution before scoring."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--query",action="append",required=True)
    p.add_argument("--country",default="fr")
    p.add_argument("--app-limit",type=int,default=20)
    p.add_argument("--hn-limit",type=int,default=20)
    p.add_argument("--reviews",type=int,default=2)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if not 1 <= args.app_limit <= 50 or not 1 <= args.hn_limit <= 100:
        p.error("invalid limits")
    result=run(args.query,args.country,args.app_limit,args.hn_limit,args.reviews)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"apps":result["app_count"],"discussions":result["hn_discussions"],"reviews":result["review_count"],"errors":len(result["errors"]),"output":str(args.output)}))
    if result["app_count"]==0 and result["hn_discussions"]==0:
        raise SystemExit(2)

if __name__=="__main__":main()
