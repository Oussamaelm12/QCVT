#!/usr/bin/env python3
"""Broad-market opportunity intelligence: diverse, bounded, auditable scans.
No autonomous payments, installs, account writes or profit predictions.
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from discover import run

SECTORS = {
 "personal_finance": ["expense tracker","subscription reminder","invoice organizer"],
 "health_wellness": ["habit tracker","meal planner","sleep routine"],
 "education": ["language learning","study planner","flashcard app"],
 "career": ["job application tracker","interview preparation","resume builder"],
 "creator_economy": ["content calendar","video caption","creator analytics"],
 "ecommerce": ["product listing","inventory tracker","shop analytics"],
 "marketing": ["seo audit","social media scheduling","email marketing"],
 "sales": ["crm app","sales pipeline","proposal builder"],
 "productivity": ["time tracking","meeting notes","task management"],
 "home_family": ["family organizer","household chores","home maintenance"],
 "travel": ["trip planner","packing list","travel budget"],
 "small_business": ["appointment booking","receipt scanner","business expense"],
 "ai_workflows": ["ai automation","ai writing","ai assistant"],
 "privacy_security": ["password manager","privacy tracker","data removal"],
 "community": ["community management","event organizer","membership app"],
 "operations": ["shift scheduling","workflow checklist","maintenance tracker"]
}
STRATEGY_LENSES = [
 "pain_and_frequency","organic_distribution","pricing_and_unit_economics",
 "competitive_moat","retention_and_switching_cost","platform_dependency",
 "regulatory_and_privacy_risk","market_timing","ai_automation_leverage",
 "partnerships_and_affiliates","conversion_and_onboarding","internationalization",
 "distribution_arbitrage","seo_and_content","product_led_growth",
 "creator_and_community","bundling_and_unbundling","b2b_self_serve"
]

def plan(sectors=None, max_queries=24, rotation=0):
    if not 1<=max_queries<=48: raise ValueError("max_queries must be 1..48")
    selected=list(sectors) if sectors is not None else list(SECTORS)
    if not selected or len(set(selected))!=len(selected) or any(s not in SECTORS for s in selected):
        raise ValueError("unknown or duplicate sectors")
    if not isinstance(rotation,int) or rotation<0: raise ValueError("rotation must be a nonnegative integer")
    # Rotate starting sector and query depth for weekly coverage without random drift.
    offset=rotation%len(selected)
    selected=selected[offset:]+selected[:offset]
    depth=rotation//len(selected)%3
    # Round robin across sectors avoids over-focusing on one familiar niche.
    queries=[]
    for idx in range(3):
        for sector in selected:
            if len(queries)>=max_queries: break
            queries.append({"sector":sector,"query":SECTORS[sector][(idx+depth)%3]})
        if len(queries)>=max_queries:break
    return queries

def scan(sectors=None,country="fr",max_queries=24,run_fn=run,pause=1,rotation=0):
    selection=plan(sectors,max_queries,rotation=rotation)
    groups=[selection[i:i+5] for i in range(0,len(selection),5)]
    reports=[];errors=[]
    for batch in groups:
        terms=[x["query"] for x in batch]
        try:
            result=run_fn(terms,country=country,app_limit=10,hn_limit=10,review_limit=1,pause=pause)
            reports.append({"sectors":list(dict.fromkeys(x["sector"] for x in batch)),
                            "queries":terms,"result":result})
            errors.extend(result.get("errors",[]))
        except (ValueError,OSError,RuntimeError,json.JSONDecodeError) as exc:
            errors.append({"queries":terms,"error":str(exc)[:200]})
    observed={"apps":sum(b["result"].get("app_count",0) for b in reports),
              "discussions":sum(b["result"].get("hn_discussions",0) for b in reports),
              "reviews":sum(b["result"].get("review_count",0) for b in reports)}
    return {
        "rotation":rotation,"observed_counts":observed,
        "completed_batches":len(reports),"failed_or_partial_errors":len(errors),
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "scope":"broad market discovery, not exhaustive global coverage",
        "country":country,"strategy_lenses":STRATEGY_LENSES,
        "planned_queries":selection,"batches":reports,"errors":errors,
        "validated_opportunities":0,
        "decision":"RESEARCH ONLY: manual evidence review, market sizing and user tests required",
        "coverage_warning":"Fixed sample of sectors and queries. Other niches, channels, regions and new strategies may be missed."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sector",action="append",choices=list(SECTORS))
    p.add_argument("--country",choices=["fr","us","de","gb"],default="fr")
    p.add_argument("--max-queries",type=int,default=24)
    p.add_argument("--rotation",type=int,default=0)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=scan(a.sector,a.country,a.max_queries,rotation=a.rotation)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"queries":len(result["planned_queries"]),"batches":len(result["batches"]),"errors":len(result["errors"]),"output":str(a.output)}))
    if not result["batches"]:raise SystemExit(2)

if __name__=="__main__":main()
