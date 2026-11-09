#!/usr/bin/env python3
"""Multi-query Apple App Store research. Read-only, stdlib-only, no revenue guesses."""
import argparse
import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

API = "https://itunes.apple.com/search"
MAX_BYTES = 2_000_000

def search(term, country="us", limit=30, opener=None):
    if not isinstance(term, str) or not 2 <= len(term.strip()) <= 100:
        raise ValueError("term must contain 2–100 characters")
    if not re.fullmatch("[A-Za-z]{2}", country) or not 1 <= limit <= 50:
        raise ValueError("invalid country or limit")
    url = API + "?" + urllib.parse.urlencode({"term":term,"country":country.lower(),"media":"software","entity":"software","limit":limit})
    request = urllib.request.Request(url, headers={"User-Agent":"OpportunityRadar/0.4","Accept":"application/json"})
    with (opener or urllib.request.urlopen)(request, timeout=15) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("response too large")
    obj = json.loads(raw)
    if not isinstance(obj, dict) or not isinstance(obj.get("results"), list):
        raise ValueError("unexpected API response")
    apps = []
    for a in obj["results"]:
        if not isinstance(a, dict) or a.get("wrapperType") != "software" or not isinstance(a.get("trackId"), int):
            continue
        apps.append({"id":a["trackId"],"name":a.get("trackName"),"publisher":a.get("artistName"),"url":a.get("trackViewUrl"),"rating":a.get("averageUserRating"),"rating_count":a.get("userRatingCount"),"price":a.get("price"),"currency":a.get("currency"),"genres":a.get("genres",[]),"description_excerpt":str(a.get("description",""))[:600]})
    return {"source_url":url,"apps":apps}

def research(queries, country="us", limit=30, pause=1.0, search_fn=search):
    if not 1 <= len(queries) <= 10 or len(set(q.strip().casefold() for q in queries)) != len(queries):
        raise ValueError("provide 1–10 unique queries")
    found, failures = {}, []
    for idx, q in enumerate(queries):
        try:
            result = search_fn(q, country=country, limit=limit)
            for a in result["apps"]:
                item = found.setdefault(a["id"], {**a, "matched_queries":[], "source_urls":[]})
                if q not in item["matched_queries"]:
                    item["matched_queries"].append(q)
                if result["source_url"] not in item["source_urls"]:
                    item["source_urls"].append(result["source_url"])
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            failures.append({"query":q,"error_type":type(exc).__name__,"detail":str(exc)[:200]})
        if idx < len(queries)-1 and pause:
            time.sleep(pause)
    apps = sorted(found.values(), key=lambda a:(-len(a["matched_queries"]),-(a.get("rating_count") or 0),a["id"]))
    return {"generated_at":datetime.now(timezone.utc).isoformat(),"country":country.lower(),"queries":queries,"source":"Apple iTunes Search API","failed_queries":failures,"unique_apps":len(apps),"apps":apps,"observed":"Search matches, ratings, prices and metadata only","not_observed":"Downloads, revenue, market size, demand or profitability","warning":"Search appearance is not market share or evidence of willingness to pay"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query",action="append",required=True)
    p.add_argument("--country",default="us")
    p.add_argument("--limit",type=int,default=30)
    p.add_argument("--pause",type=float,default=1.0)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.pause < 0.5:
        p.error("minimum request pause: 0.5s")
    result=research(args.query,args.country,args.limit,args.pause)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(args.output),"unique_apps":result["unique_apps"],"failed_queries":len(result["failed_queries"])}))

if __name__=="__main__":
    main()
