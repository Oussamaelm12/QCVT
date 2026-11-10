#!/usr/bin/env python3
"""Evidence-linked innovation worksheets: benchmark, JTBD, C-K, TRIZ, Blue Ocean and tests.

This module validates and formats SUBMITTED research and concepts. It does not
independently browse, interview customers or invent a commercially proven idea.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

METHODS = {
 "benchmark": {"stage":"research","purpose":"Compare existing alternatives using matched criteria, primary sources and gaps."},
 "jtbd": {"stage":"research","purpose":"Identify the customer's situation, desired progress, workaround and measurable struggle."},
 "design_thinking": {"stage":"research_strategy_validation","purpose":"Empathize, define, ideate, prototype and test; use actual user observations."},
 "ck": {"stage":"strategy","purpose":"Expand concept (C) and knowledge (K) spaces, identify missing knowledge and experiments."},
 "triz": {"stage":"strategy","purpose":"State a real trade-off, then explore ways to resolve it without assuming a technical breakthrough."},
 "scamper": {"stage":"strategy","purpose":"Create deliberate alternatives; screen for customer value, not novelty alone."},
 "blue_ocean": {"stage":"strategy","purpose":"Eliminate, reduce, raise and create value factors against actual alternatives."},
 "lean_startup": {"stage":"validation","purpose":"Pre-register a falsifiable offer experiment with a measurable commitment and stop rule."},
 "aarrr": {"stage":"launch","purpose":"Measure acquisition, activation, retention, referral and revenue after approved launch."}
}

def nonempty(v):
 return isinstance(v,str) and bool(v.strip())

def check_ids(rows,label):
 if not isinstance(rows,list): raise ValueError(label+" must be a list")
 ids=set()
 for row in rows:
  if not isinstance(row,dict) or not nonempty(row.get("id")):raise ValueError(label+" row requires id")
  if row["id"] in ids:raise ValueError("duplicate "+label+" id")
  ids.add(row["id"])
 return ids

def valid_url(value):
 try:
  p=urlparse(value)
  return p.scheme=="https" and bool(p.hostname) and not p.username and not p.password
 except (TypeError,ValueError):return False

def evaluate(data):
 if not isinstance(data,dict) or not nonempty(data.get("subject")):raise ValueError("subject required")
 source_ids=check_ids(data.get("sources",[]),"sources")
 finding_ids=check_ids(data.get("findings",[]),"findings")
 competitor_ids=check_ids(data.get("competitors",[]),"competitors")
 concept_ids=check_ids(data.get("concepts",[]),"concepts")
 for s in data.get("sources",[]):
  if not valid_url(s.get("url")):raise ValueError("source needs HTTPS URL")
 for f in data.get("findings",[]):
  if not isinstance(f.get("source_ids",[]),list) or not set(f.get("source_ids",[])).issubset(source_ids):
   raise ValueError("finding references missing sources")
 for c in data.get("competitors",[]):
  if not isinstance(c.get("attributes",{}),dict):raise ValueError("attributes must be an object")
  if not isinstance(c.get("source_ids",[]),list) or not set(c.get("source_ids",[])).issubset(source_ids):
   raise ValueError("competitor references missing sources")
 for c in data.get("concepts",[]):
  if not isinstance(c.get("finding_ids",[]),list) or not set(c.get("finding_ids",[])).issubset(finding_ids):
   raise ValueError("concept references missing findings")
 for entry in data.get("jtbd",[]):
  if not isinstance(entry,dict) or not set(entry.get("finding_ids",[])).issubset(finding_ids):
   raise ValueError("JTBD references missing findings")
 for node in data.get("ck_nodes",[]):
  if not isinstance(node,dict) or node.get("space") not in ("C","K"):
   raise ValueError("C-K nodes must declare C or K")
  if not set(node.get("finding_ids",[])).issubset(finding_ids):raise ValueError("C-K unknown finding")
 for t in data.get("tests",[]):
  if not isinstance(t,dict) or t.get("concept_id") not in concept_ids:raise ValueError("test requires known concept")
 for k in ("jtbd","ck_nodes","tests","contradictions","blue_ocean_factors"):
  if not isinstance(data.get(k,[]),list):raise ValueError(k+" must be a list")
 sources={s["id"]:s for s in data.get("sources",[])}
 def grounded(ids):
  return bool(ids) and all(sources[x].get("review_status")=="manually_checked" for x in ids)
 benchmark=[]
 for c in data.get("competitors",[]):
  benchmark.append({"id":c["id"],"name":c.get("name",""),"attributes":c.get("attributes",{}),
                    "source_ids":c.get("source_ids",[]),
                    "source_reviewed":grounded(c.get("source_ids",[]))})
 return {
  "subject":data["subject"],"method_catalog":METHODS,
  "benchmark":benchmark,
  "benchmark_complete":len(benchmark)>=3 and all(c["source_reviewed"] for c in benchmark),
  "jtbd":[{"statement":x.get("statement",""),"finding_ids":x.get("finding_ids",[]),
           "has_support":bool(x.get("finding_ids"))} for x in data.get("jtbd",[])],
  "ck_nodes":[{"space":x["space"],"statement":x.get("statement",""),
               "parent_id":x.get("parent_id"),"finding_ids":x.get("finding_ids",[]),
               "status":"concept_hypothesis" if x["space"]=="C" else "knowledge_to_verify"}
              for x in data.get("ck_nodes",[])],
  "contradictions":data.get("contradictions",[]),
  "blue_ocean_factors":data.get("blue_ocean_factors",[]),
  "concepts":[{"id":c["id"],"name":c.get("name",""),"finding_ids":c.get("finding_ids",[]),
               "status":"HYPOTHESIS; not validated"} for c in data.get("concepts",[])],
  "tests":[{"concept_id":t["concept_id"],
            "preregistered":all(nonempty(t.get(x)) for x in ("target_customer","test_method","success_threshold","stop_rule","duration","cost_ceiling")),
            "actual_outcome":"UNKNOWN; must be collected separately"} for t in data.get("tests",[])],
  "limitations":["Source review flags are self-reported, not automatically verified.",
                 "Competitor attributes and pricing are user-supplied; not fact-checked.",
                 "C-K exploration here is a traceable worksheet, not autonomous ideation.",
                 "No paid demand, innovation superiority or commercial success is inferred."]
 }

def markdown(result):
 lines=["# Innovation & Competitive Intelligence — "+result["subject"],"",
        "## Method routing", "| Method | Stage | Purpose |","|---|---|---|"]
 for name,m in METHODS.items():lines.append("| "+name+" | "+m["stage"]+" | "+m["purpose"]+" |")
 lines+=["","## Benchmark (observations only; no invented scores)",
         "| Alternative | Attributes as supplied | Reviewed source flag |",
         "|---|---|---|"]
 for c in result["benchmark"]:
  lines.append("| "+str(c["name"]).replace("|","/")+" | "+", ".join(str(k)+": "+str(v) for k,v in c["attributes"].items()).replace("|","/")+" | "+str(c["source_reviewed"])+" |")
 lines+=["","Benchmark completeness gate: "+("MET (minimum, not proof)" if result["benchmark_complete"] else "BLOCKED — requires 3 reviewed alternatives"),"",
         "## JTBD — jobs and struggle"]
 lines += ["- "+x["statement"]+" (finding refs: "+", ".join(x["finding_ids"])+")" for x in result["jtbd"]]
 lines+=["","## C-K expansion — concepts versus knowledge"]
 lines += ["- ["+x["space"]+"] "+str(x["statement"])+" | status: "+x["status"]+" | parent: "+str(x["parent_id"] or "root") for x in result["ck_nodes"]]
 lines+=["","## TRIZ contradictions / trade-offs"]
 lines += ["- "+str(x) for x in result["contradictions"]]
 lines+=["","## Blue Ocean eliminate / reduce / raise / create"]
 lines += ["- "+str(x) for x in result["blue_ocean_factors"]]
 lines+=["","## Innovation concepts"]
 lines += ["- "+c["id"]+": "+c["name"]+" — "+c["status"] for c in result["concepts"]]
 lines+=["","## Lean test preregistration"]
 lines += ["- "+x["concept_id"]+": "+("READY FOR REVIEW" if x["preregistered"] else "INCOMPLETE")+
           "; actual result: "+x["actual_outcome"] for x in result["tests"]]
 lines+=["","## Integrity limits"]+["- "+x for x in result["limitations"]]
 return "\n".join(lines)+"\n"

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",required=True,type=Path)
 p.add_argument("--output-dir",required=True,type=Path)
 args=p.parse_args()
 result=evaluate(json.loads(args.input.read_text(encoding="utf-8")))
 args.output_dir.mkdir(parents=True,exist_ok=True)
 (args.output_dir/"INNOVATION_DOSSIER.md").write_text(markdown(result),encoding="utf-8")
 (args.output_dir/"INNOVATION_ASSESSMENT.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"benchmark_complete":result["benchmark_complete"],"concepts":len(result["concepts"]),"test_cards":len(result["tests"])}))
if __name__=="__main__":main()
