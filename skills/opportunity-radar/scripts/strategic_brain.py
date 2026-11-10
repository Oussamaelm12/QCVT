#!/usr/bin/env python3
"""Private Strategic Business Brain: offline portfolio arbitration + append-only decision log.

Market evaluation only uses explicitly supplied EXTERNAL market evidence.
Private execution constraints are isolated and never change market ranking.
No API calls, LLM, external actions or automatic business recommendations.
"""
import argparse
import hashlib
import json
import math
import os
import re
from datetime import datetime,timezone
from pathlib import Path
from decision_engine import evaluate as evaluate_market

DIMENSIONS=("pain","demand","distribution","economics","feasibility","competition","risk")
SCHEMA_VERSION="1.0"
MAX_INPUT_BYTES=2_000_000
def load(path):
 p=Path(path)
 if p.stat().st_size>MAX_INPUT_BYTES:raise ValueError("input exceeds 2MB")
 d=json.loads(p.read_text(encoding="utf-8"))
 if not isinstance(d,dict):raise ValueError("JSON object required")
 return d

def validate_portfolio(data):
 if not isinstance(data,dict) or not isinstance(data.get("businesses"),list):raise ValueError("businesses array required")
 seen=set()
 for b in data["businesses"]:
  if not isinstance(b,dict):raise ValueError("invalid business")
  bid=b.get("id")
  if not isinstance(bid,str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,48}",bid) or bid in seen:
   raise ValueError("invalid or duplicate business id")
  seen.add(bid)
  if not isinstance(b.get("market"),dict):raise ValueError("market object required")
  if not isinstance(b["market"].get("title"),str) or not b["market"]["title"].strip():raise ValueError("market title required")
  if "personal_profile" in b or "personal_profile" in b["market"]:
   raise ValueError("personal profile is prohibited as a market input")
 return data

def analyze(data, execution_constraints=None):
 validate_portfolio(data)
 if execution_constraints is not None and not isinstance(execution_constraints,dict):
  raise ValueError("constraints must be object")
 market=[]
 for b in data["businesses"]:
  result=evaluate_market(b["market"])
  market.append({"id":b["id"],"title":result["title"],"market_score":result["score"],
                 "market_status":result["status"],"source_domains":result["independent_domains"],
                 "missing_dimensions":result["missing_dimensions"],
                 "recommendation":result["recommendation"],
                 "direct_customer_signal":result["direct_customer_signal"],
                 "score_cap":result["score_cap"],
                 "evidence_count":len(result["accepted_evidence"])})
 market.sort(key=lambda x:(-x["market_score"],-x["source_domains"],x["id"]))
 # These are informational resource-fit checks, NOT a re-ranking.
 feasibility={}
 if execution_constraints:
  budget=execution_constraints.get("budget_eur")
  hours=execution_constraints.get("hours_per_week")
  if budget is not None and (type(budget) not in (int,float) or not math.isfinite(budget) or budget<0):
   raise ValueError("budget_eur must be a nonnegative finite number")
  if hours is not None and (type(hours) not in (int,float) or not math.isfinite(hours) or hours<0):
   raise ValueError("hours_per_week must be a nonnegative finite number")
  estimates=execution_constraints.get("estimates",{})
  if not isinstance(estimates,dict):raise ValueError("estimates must be object")
  for b in data["businesses"]:
   e=estimates.get(b["id"],{})
   if not isinstance(e,dict):raise ValueError("estimate must be object")
   cost=e.get("estimated_test_cost_eur")
   time=e.get("estimated_test_hours")
   for v in (cost,time):
    if v is not None and (type(v) not in (int,float) or not math.isfinite(v) or v<0):
     raise ValueError("estimate must be nonnegative finite number")
   feasibility[b["id"]]={"budget_fit":("UNKNOWN" if budget is None or cost is None else cost<=budget),
                          "time_fit":("UNKNOWN" if hours is None or time is None else time<=hours),
                          "estimates_are":"USER-SUPPLIED; NOT VERIFIED"}
 return {"schema_version":SCHEMA_VERSION,"generated_at":datetime.now(timezone.utc).isoformat(),
         "market_ranking":market,"execution_feasibility":feasibility,
         "strategic_notes":["Scores are capped heuristics, not probabilities of success.",
                            "Evidence URLs are syntactically checked by the market engine, NOT fact-checked.",
                            "Market ranking does not use profile, prior ventures, personal preferences or execution constraints.",
                            "Market rank and personal feasibility are intentionally separate.",
                            "No GO or revenue claim without actual experiment and economics evidence."],
         "recommended_next_action":("Collect and verify primary evidence for the leading candidates; design low-cost customer tests."
                                    if market else "Add independently researched market candidates.")}

def record_decision(path,entry):
 path=Path(path)
 if not isinstance(entry,dict):raise ValueError("entry must be object")
 required=("business_id","decision","reason","evidence_refs","next_review")
 if any(k not in entry for k in required):raise ValueError("missing decision field")
 if entry["decision"] not in ("RESEARCH","TEST","GO","PIVOT","STOP","HOLD"):raise ValueError("invalid decision")
 if not isinstance(entry["evidence_refs"],list) or any(not isinstance(x,str) for x in entry["evidence_refs"]):
  raise ValueError("evidence_refs must be list of strings")
 if not isinstance(entry["reason"],str) or not entry["reason"].strip():raise ValueError("reason required")
 from datetime import date
 try:date.fromisoformat(entry["next_review"])
 except (ValueError,TypeError):raise ValueError("next_review must be YYYY-MM-DD")
 if path.exists():
  if path.is_symlink():raise ValueError("refuse symlink")
  old=path.read_text(encoding="utf-8")
 else:old=""
 previous=old.splitlines()[-1] if old.splitlines() else ""
 previous_hash=hashlib.sha256(previous.encode("utf-8")).hexdigest() if previous else None
 row={"recorded_at":datetime.now(timezone.utc).isoformat(),"business_id":entry["business_id"],
      "decision":entry["decision"],"reason":entry["reason"],"evidence_refs":entry["evidence_refs"],
      "next_review":entry["next_review"],"previous_record_sha256":previous_hash,
      "record_status":"USER-REPORTED; not externally verified"}
 # GO is always a human decision record, never an automatic engine determination.
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("a",encoding="utf-8") as f:
  f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
  f.flush()
  os.fsync(f.fileno())
 return row

def write_new(path,data):
 path=Path(path)
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("x",encoding="utf-8") as f:json.dump(data,f,indent=2,ensure_ascii=False)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 sub=p.add_subparsers(dest="cmd",required=True)
 a=sub.add_parser("arbitrate")
 a.add_argument("--portfolio",type=Path,required=True)
 a.add_argument("--constraints",type=Path)
 a.add_argument("--output",type=Path,required=True)
 d=sub.add_parser("record-decision")
 d.add_argument("--journal",type=Path,required=True)
 d.add_argument("--entry",type=Path,required=True)
 args=p.parse_args()
 if args.cmd=="arbitrate":
  r=analyze(load(args.portfolio),load(args.constraints) if args.constraints else None)
  write_new(args.output,r)
  print(json.dumps({"businesses":len(r["market_ranking"]),"output":str(args.output),
                    "no_external_actions":True}))
 else:print(json.dumps(record_decision(args.journal,load(args.entry)),ensure_ascii=False))
if __name__=="__main__":main()
