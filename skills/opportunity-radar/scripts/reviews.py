#!/usr/bin/env python3
"""Read-only Apple customer-review RSS (JSON), with source provenance.
No sentiment inference or fake revenue/download numbers.
"""
import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAX_BYTES = 2_000_000

def fetch_reviews(app_id, country="us", page=1, opener=None):
    app_id = str(app_id)
    if not re.fullmatch(r"[0-9]{1,15}", app_id):
        raise ValueError("app_id must be numeric")
    if not re.fullmatch(r"[A-Za-z]{2}", country):
        raise ValueError("country must be two letters")
    if not isinstance(page,int) or isinstance(page,bool) or not 1 <= page <= 10:
        raise ValueError("page must be 1..10")
    url = f"https://itunes.apple.com/{country.lower()}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
    req = urllib.request.Request(url, headers={"User-Agent":"OpportunityRadar/0.6","Accept":"application/json"})
    with (opener or urllib.request.urlopen)(req, timeout=15) as response:
        raw = response.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:
        raise ValueError("response too large")
    data=json.loads(raw)
    feed=data.get("feed",{}) if isinstance(data,dict) else {}
    entries=feed.get("entry",[]) if isinstance(feed,dict) else []
    if isinstance(entries,dict):
        entries=[entries]
    if not isinstance(entries,list):
        raise ValueError("unexpected review feed")
    reviews=[]
    for e in entries:
        if not isinstance(e,dict) or "im:rating" not in e:
            continue
        def label(field):
            obj=e.get(field,{})
            return str(obj.get("label","")) if isinstance(obj,dict) else ""
        try:
            rating=int(label("im:rating"))
        except ValueError:
            continue
        if not 1<=rating<=5:
            continue
        reviews.append({
            "review_id":label("id"),"rating":rating,
            "title":label("title")[:250],"text":label("content")[:2000],
            "updated_at":label("updated"),"source_url":url,
        })
    return {
        "source":"Apple customer reviews RSS",
        "app_id":app_id,"country":country.lower(),"page":page,
        "retrieved_at":datetime.now(timezone.utc).isoformat(),
        "source_url":url,"reviews":reviews,
        "disclaimer":"A recent review sample is not representative of all users; user complaints require interpretation and cross-checking."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("app_id")
    p.add_argument("--country",default="us")
    p.add_argument("--page",type=int,default=1)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=fetch_reviews(a.app_id,a.country,a.page)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(a.output),"reviews":len(result["reviews"])}))

if __name__=="__main__":
    main()
