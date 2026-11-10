#!/usr/bin/env python3
"""Opt-in source adapters: Google Trends via SerpApi and Reddit OAuth.
No credentials stored, no unapproved paid calls. Both adapters are read-only.
"""
import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

MAX_BYTES = 2_000_000

def _read_json(url, headers, opener=None):
    request=urllib.request.Request(url,headers=headers)
    with (opener or urllib.request.urlopen)(request,timeout=15) as response:
        raw=response.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES: raise ValueError("response too large")
    return json.loads(raw)

def google_trends(term, geography="FR", *, allow_paid=False, api_key=None, opener=None):
    if not allow_paid: raise PermissionError("Paid/credit-consuming SerpApi access requires explicit approval")
    key=api_key or os.environ.get("SERPAPI_KEY")
    if not key: raise RuntimeError("SERPAPI_KEY is not configured")
    if not isinstance(term,str) or not 2<=len(term.strip())<=100: raise ValueError("invalid term")
    if not re.fullmatch("[A-Za-z]{2}",geography): raise ValueError("invalid geography")
    # Do not include API keys in source URLs saved to reports.
    url="https://serpapi.com/search.json?"+urllib.parse.urlencode({
        "engine":"google_trends","q":term,"geo":geography.upper(),
        "data_type":"TIMESERIES","api_key":key})
    data=_read_json(url,{"Accept":"application/json","User-Agent":"OpportunityRadar/0.7"},opener)
    if not isinstance(data,dict): raise ValueError("invalid trends response")
    if "error" in data: raise RuntimeError("Trends provider returned an error")
    timeline=data.get("interest_over_time",{}).get("timeline_data",[])
    if not isinstance(timeline,list): timeline=[]
    points=[]
    for p in timeline:
        if not isinstance(p,dict): continue
        values=p.get("values",[])
        if not isinstance(values,list) or not values: continue
        try: value=int(values[0].get("extracted_value"))
        except (TypeError,ValueError,AttributeError): continue
        points.append({"date":p.get("date"),"relative_index":value})
    return {"source":"Google Trends via SerpApi","query":term,"geography":geography.upper(),
            "retrieved_at":datetime.now(timezone.utc).isoformat(),"points":points,
            "source_url":"https://trends.google.com/trends/explore",
            "warning":"Relative search interest (0–100), NOT search volume; SerpApi may consume paid credits."}

def reddit_search(term, *, token=None, user_agent=None, limit=25, opener=None):
    token=token or os.environ.get("REDDIT_ACCESS_TOKEN")
    user_agent=user_agent or os.environ.get("REDDIT_USER_AGENT")
    if not token or not user_agent: raise RuntimeError("Reddit OAuth token and descriptive user-agent required")
    if not isinstance(term,str) or not 2<=len(term.strip())<=100 or not 1<=limit<=50:
        raise ValueError("invalid search parameters")
    url="https://oauth.reddit.com/search?"+urllib.parse.urlencode({
        "q":term,"sort":"new","t":"month","limit":limit,"type":"link"})
    data=_read_json(url,{"Authorization":"Bearer "+token,"User-Agent":user_agent,"Accept":"application/json"},opener)
    children=data.get("data",{}).get("children",[]) if isinstance(data,dict) else []
    if not isinstance(children,list): raise ValueError("invalid Reddit response")
    posts=[]
    for child in children:
        d=child.get("data",{}) if isinstance(child,dict) else {}
        pid=d.get("id")
        if not isinstance(pid,str) or not re.fullmatch("[a-z0-9]+",pid): continue
        posts.append({"id":pid,"title":str(d.get("title",""))[:300],
                      "excerpt":str(d.get("selftext",""))[:1000],
                      "created_utc":d.get("created_utc"),"score":d.get("score"),
                      "comments":d.get("num_comments"),
                      "url":"https://www.reddit.com"+str(d.get("permalink","")) if str(d.get("permalink","")).startswith("/r/") else "https://www.reddit.com/comments/"+pid})
    return {"source":"Reddit OAuth API","query":term,"retrieved_at":datetime.now(timezone.utc).isoformat(),
            "posts":posts,"source_url":"https://www.reddit.com/search/",
            "warning":"Posts are self-selected anecdotes, not verified buying intent."}
