#!/usr/bin/env python3
"""Production CLI: deterministic research dossier with JSON + Markdown outputs.
Free sources by default; no credentials, paid calls, or external writes.
"""
import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from discover import run

def markdown(dossier):
    q=", ".join(dossier["queries"])
    lines=[
        "# Opportunity Radar — research dossier",
        "",
        f"Generated (UTC): {dossier['generated_at']}",
        f"Market: {dossier['country'].upper()} | Queries: {q}",
        "",
        "## Coverage",
        f"- App Store listings: {dossier['app_count']}",
        f"- Hacker News discussions: {dossier['hn_discussions']}",
        f"- App Store reviews: {dossier['review_count']}",
        f"- Source/API errors: {len(dossier['errors'])}",
        "",
        "## Candidate competitors (observed listings, not validated opportunities)",
    ]
    for a in dossier["app_results"][:20]:
        name=str(a.get("name") or "Unnamed").replace("\n"," ")[:100]
        url=a.get("url")
        if isinstance(url,str) and url.startswith("https://"):
            lines.append(f"- {name} — {url}")
        else: lines.append(f"- {name} — URL unavailable")
    lines.extend(["","## Discussions (not proof of purchasing demand)"])
    for d in dossier["discussion_results"][:20]:
        title=str(d.get("title") or "Untitled").replace("\n"," ")[:150]
        lines.append(f"- {title} — {d['discussion_url']}")
    lines.extend(["","## Review sample (non-representative)"])
    for batch in dossier["review_results"][:5]:
        lines.append(f"- App ID: {batch.get('app_id','unknown')}; reviews sampled: {len(batch.get('reviews',[]))}; source: {batch.get('source_url','unknown')}")
    lines.extend(["","## Limitations",
        "- No verified market size, search volume, willingness to pay, churn, or customer acquisition cost.",
        "- App listings, reviews, and community mentions are research leads, not independent validation of a business.",
        "- No paid calls, publishing, or autonomous third-party skill execution.",
        "- Research can be incomplete because APIs are rate-limited or unavailable.",
        "","## Next decision",
        "Review repeated concrete complaints, independent corroboration, competitor pricing and organic acquisition feasibility before any build/no-build recommendation.",
    ])
    if dossier["errors"]:
        lines.extend(["","## Partial failures"])
        for e in dossier["errors"][:20]:
            lines.append(f"- {str(e.get('source','unknown'))[:40]}: {str(e.get('error','unknown'))[:180]}")
    return "\n".join(lines)+"\n"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query",action="append",required=True)
    p.add_argument("--country",default="fr")
    p.add_argument("--output-dir",type=Path,default=Path("research/output"))
    p.add_argument("--app-limit",type=int,default=20)
    p.add_argument("--hn-limit",type=int,default=20)
    p.add_argument("--reviews",type=int,default=2)
    a=p.parse_args()
    if not 1<=a.app_limit<=50 or not 1<=a.hn_limit<=100:
        p.error("invalid result limits")
    if not 0<=a.reviews<=5:p.error("reviews must be 0..5")
    if not re.fullmatch("[a-zA-Z]{2}",a.country):p.error("country must be ISO two-letter code")
    dossier=run(a.query,country=a.country,app_limit=a.app_limit,hn_limit=a.hn_limit,review_limit=a.reviews)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    (a.output_dir/"dossier.json").write_text(json.dumps(dossier,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (a.output_dir/"REPORT.md").write_text(markdown(dossier),encoding="utf-8")
    print(json.dumps({"json":str(a.output_dir/"dossier.json"),"report":str(a.output_dir/"REPORT.md"),"apps":dossier["app_count"],"discussions":dossier["hn_discussions"],"reviews":dossier["review_count"],"errors":len(dossier["errors"])}))
    if dossier["app_count"]==0 and dossier["hn_discussions"]==0:raise SystemExit(2)

if __name__=="__main__":main()
