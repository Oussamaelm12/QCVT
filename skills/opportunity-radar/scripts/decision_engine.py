#!/usr/bin/env python3
"""Conservative, explainable decision engine. No invented demand or profits."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse

DIMENSIONS=("pain","demand","distribution","economics","feasibility","competition","risk")
WEIGHTS={"pain":25,"demand":20,"distribution":20,"economics":15,"feasibility":10,"competition":5,"risk":5}
ALLOWED_KINDS={"app_listing","review","community_post","search_metric","payment","interview","experiment","competitor_pricing"}
def normalize_url(url):
    if not isinstance(url,str):return None
    try:
        p=urlparse(url)
        if p.scheme!="https" or not p.hostname or p.username or p.password:return None
        return p.hostname.lower()
    except ValueError:return None

def evaluate(candidate):
    if not isinstance(candidate,dict) or not isinstance(candidate.get("title"),str) or not candidate["title"].strip():
        raise ValueError("candidate title required")
    ratings=candidate.get("ratings",{})
    if not isinstance(ratings,dict):raise ValueError("ratings must be object")
    if any(k not in DIMENSIONS for k in ratings):raise ValueError("unknown dimension")
    for k,v in ratings.items():
        if type(v) not in (int,float) or not 0<=v<=5:raise ValueError("ratings must be 0..5")
    evidence=candidate.get("evidence",[])
    if not isinstance(evidence,list):raise ValueError("evidence must be list")
    accepted=[];rejected=[]
    for e in evidence:
        if not isinstance(e,dict):rejected.append("invalid evidence object");continue
        domain=normalize_url(e.get("url"))
        if e.get("kind") not in ALLOWED_KINDS or not domain or not isinstance(e.get("observed_at"),str) or not e["observed_at"].strip():
            rejected.append("missing source, kind or observation date");continue
        accepted.append({"kind":e["kind"],"url":e["url"],"domain":domain,"observed_at":e["observed_at"],"claim":str(e.get("claim",""))[:300]})
    independent=len({x["domain"] for x in accepted})
    kinds={x["kind"] for x in accepted}
    direct=bool(kinds & {"payment","interview","experiment"})
    observed=bool(kinds & {"review","community_post","search_metric"})
    raw=sum(WEIGHTS[k]*ratings.get(k,0)/5 for k in DIMENSIONS)
    # A score is a prioritization heuristic, NOT probability of commercial success.
    missing=[k for k in DIMENSIONS if k not in ratings]
    if not accepted:status="UNSUPPORTED"
    elif independent<2 or not observed:status="DISCOVERY"
    elif not direct:status="RESEARCH"
    else:status="TESTED_SIGNAL"
    if missing or independent<2:cap=35
    elif not direct:cap=65
    else:cap=100
    score=round(min(raw,cap),1)
    return {"title":candidate["title"].strip(),"score":score,"raw_heuristic":round(raw,1),
            "status":status,"independent_domains":independent,"direct_customer_signal":direct,
            "missing_dimensions":missing,"accepted_evidence":accepted,"rejected_evidence":rejected,
            "score_cap":cap,"recommendation":("COLLECT EVIDENCE" if status in ("UNSUPPORTED","DISCOVERY") else "RUN CUSTOMER TEST" if status=="RESEARCH" else "REVIEW TEST RESULTS"),
            "disclaimer":"Heuristic prioritization only; not proof of demand, profitability or revenue."}

def rank(candidates):
    if not isinstance(candidates,list):raise ValueError("expected candidate list")
    results=[evaluate(x) for x in candidates]
    return sorted(results,key=lambda x:(-x["score"],-x["independent_domains"],x["title"]))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    data=json.loads(a.input.read_text(encoding="utf-8"))
    if not isinstance(data,dict) or not isinstance(data.get("candidates"),list):p.error("input requires candidates array")
    result={"generated_at":datetime.now(timezone.utc).isoformat(),"ranking":rank(data["candidates"]),"policy":"No paid API calls or external writes"}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"candidates":len(result["ranking"]),"output":str(a.output)}))
if __name__=="__main__":main()
