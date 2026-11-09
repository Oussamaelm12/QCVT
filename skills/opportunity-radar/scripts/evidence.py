#!/usr/bin/env python3
"""Fuse source exports into an auditable market evidence dossier.
This is a data inventory, NOT automated pain classification or demand validation.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SUPPORTED = {"Apple iTunes Search API", "Hacker News via Algolia public API"}

def _valid_http_url(url):
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.hostname)

def merge(documents):
    inventory = []
    seen = set()
    issues = []
    for index, doc in enumerate(documents):
        source = doc.get("source")
        if source not in SUPPORTED:
            issues.append({"input":index,"problem":"unsupported source"})
            continue
        records = doc.get("apps") if source == "Apple iTunes Search API" else doc.get("results")
        if not isinstance(records,list):
            issues.append({"input":index,"problem":"missing records"})
            continue
        for item in records:
            if not isinstance(item,dict):
                continue
            if source == "Apple iTunes Search API":
                key = ("apple",str(item.get("id") or item.get("app_id") or ""))
                url = item.get("url")
                title = item.get("name")
                kind = "competitor_listing"
            else:
                key = ("hn",str(item.get("id") or ""))
                url = item.get("discussion_url")
                title = item.get("title")
                kind = "community_discussion"
            if not key[1] or not _valid_http_url(url):
                issues.append({"input":index,"problem":"record missing stable id or HTTPS URL"})
                continue
            if key in seen:
                continue
            seen.add(key)
            inventory.append({
                "source":source,"kind":kind,"title":title,"url":url,
                "source_record_id":key[1],"evidence_class":"UNREVIEWED",
                "note":"Requires human review. Listing/discussion alone is not demonstrated demand."
            })
    sources = sorted({i["source"] for i in inventory})
    return {
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "status":"EVIDENCE INVENTORY ONLY — NOT MARKET VALIDATION",
        "sources":sources,
        "source_count":len(sources),
        "record_count":len(inventory),
        "records":inventory,
        "issues":issues,
        "validation_ready":False,
        "next_step":"Read individual sources; identify and independently corroborate concrete pain, pricing and organic acquisition signals."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("inputs",nargs="+",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    documents=[json.loads(path.read_text(encoding="utf-8")) for path in args.inputs]
    result=merge(documents)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(args.output),"records":result["record_count"],"sources":result["sources"]}))

if __name__=="__main__": main()
