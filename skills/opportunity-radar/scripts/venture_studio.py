#!/usr/bin/env python3
"""Opportunity Radar -> Evidence Lab -> Strategy Lab -> Execution Board.

Deterministic, offline artifact generator. It DOES NOT browse, call an LLM,
fact-check a URL, perform commercial experiments, or deploy a product.
"""
import argparse
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

STEPS = (
    ("select", "Select an externally researched opportunity and target market"),
    ("research", "Verify original sources, customer problem and alternatives"),
    ("strategy", "Generate and challenge differentiating concepts"),
    ("validate", "Test buying intent using a preregistered success threshold"),
    ("spec", "Choose a minimum useful scope and acceptance criteria"),
    ("build", "Implement only the validated wedge with automated tests"),
    ("launch", "Launch a controlled pilot and measure the funnel"),
    ("iterate", "Keep, improve, pivot or stop based on observed evidence"),
)
KINDS = {"primary", "industry_report", "community", "review", "competitor", "regulation"}
TAGS = {"observed", "inferred", "hypothesis", "contradicted"}
IDEA_LENSES = (
    ("Underserved workflow", "Solve the narrow, high-friction step rather than the whole category."),
    ("Cost and complexity inversion", "Remove unnecessary setup, integrations and maintenance."),
    ("Distribution-native product", "Deliver value inside an existing workflow or marketplace."),
    ("Trust and transparency", "Offer explainable results, user control and clear error handling."),
    ("Outcome-oriented pricing", "Test whether price can track measurable customer value."),
    ("Data portability", "Differentiate with painless onboarding, export and interoperability."),
)
def clean(x, limit=500):
    if not isinstance(x, str):
        return ""
    return re.sub(r"\s+", " ", x).strip()[:limit]

def domain(url):
    if not isinstance(url, str): return None
    try:
        p = urlparse(url)
        return p.hostname.lower() if p.scheme == "https" and p.hostname and not p.username and not p.password else None
    except ValueError:
        return None

def require_id(item, label):
    value = item.get("id") if isinstance(item, dict) else None
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,48}", value):
        raise ValueError(label + " needs a simple unique id")
    return value

def validate(data):
    if not isinstance(data, dict): raise ValueError("input must be a JSON object")
    for k in ("subject", "market"):
        if not clean(data.get(k)): raise ValueError(k + " is required")
    for k in ("sources", "findings", "competitors", "concepts"):
        if not isinstance(data.get(k, []), list): raise ValueError(k + " must be a list")
    ids = {}
    for name in ("sources", "findings", "concepts"):
        rows = data.get(name, [])
        seen = set()
        for item in rows:
            ident = require_id(item, name)
            if ident in seen: raise ValueError("duplicate " + name + " id: " + ident)
            seen.add(ident)
        ids[name] = seen
    for s in data.get("sources", []):
        if not domain(s.get("url")): raise ValueError("source " + s["id"] + " needs HTTPS URL")
        if s.get("kind") not in KINDS: raise ValueError("invalid source kind")
        if s.get("review_status", "unchecked") not in ("unchecked", "manually_checked"):
            raise ValueError("invalid review status")
        if s.get("review_status") == "manually_checked":
            try: date.fromisoformat(s.get("reviewed_at", ""))
            except (ValueError, TypeError): raise ValueError("manually checked source needs reviewed_at YYYY-MM-DD")
    for f in data.get("findings", []):
        if f.get("classification") not in TAGS: raise ValueError("invalid finding classification")
        refs = f.get("source_ids", [])
        if not isinstance(refs, list) or not set(refs).issubset(ids["sources"]):
            raise ValueError("finding " + f["id"] + " has unknown source refs")
    for c in data.get("concepts", []):
        refs = c.get("finding_ids", [])
        if not isinstance(refs, list) or not set(refs).issubset(ids["findings"]):
            raise ValueError("concept " + c["id"] + " has unknown finding refs")
    return data

def assess(data):
    validate(data)
    sources = {s["id"]:s for s in data.get("sources", [])}
    findings = {f["id"]:f for f in data.get("findings", [])}
    supported = set()
    ledger = []
    for f in findings.values():
        refs = [sources[x] for x in f.get("source_ids", [])]
        reviewed = [s for s in refs if s.get("review_status") == "manually_checked"]
        independent = len({domain(s["url"]) for s in reviewed})
        # Manual source review is self-reported, NOT factual verification by this program.
        corroborated = f["classification"] == "observed" and independent >= 2
        if corroborated: supported.add(f["id"])
        ledger.append({"id":f["id"], "classification":f["classification"],
                       "manually_reviewed_domains":independent,
                       "corroborated_links":corroborated,
                       "statement":clean(f.get("statement"), 1000),
                       "source_ids":f.get("source_ids", [])})
    checked = [s for s in sources.values() if s.get("review_status") == "manually_checked"]
    alternatives = [x for x in data.get("competitors", []) if clean(x.get("name")) and domain(x.get("url"))]
    research_ready = len({domain(s["url"]) for s in checked}) >= 2 and bool(supported) and bool(alternatives)
    concepts = []
    for c in data.get("concepts", []):
        backing = set(c.get("finding_ids", [])) & supported
        test_ready = bool(backing and clean(c.get("differentiation_hypothesis")) and
                          clean(c.get("smallest_test")) and clean(c.get("success_criterion")) and
                          clean(c.get("target_user")))
        concepts.append({"id":c["id"], "name":clean(c.get("name")) or c["id"],
                         "backed_by_reviewed_claim_ids":sorted(backing),
                         "test_ready":test_ready,
                         "missing":([k for k in ("target_user", "differentiation_hypothesis",
                            "smallest_test", "success_criterion") if not clean(c.get(k))] +
                            (["corroborated problem evidence"] if not backing else []))})
    return {"research_ready_for_human_review":research_ready,
            "sources_recorded":len(sources), "sources_manually_reviewed":len(checked),
            "corroborated_observations":len(supported), "competitors_recorded":len(alternatives),
            "claim_ledger":ledger, "concepts":concepts,
            "next_gate":("HUMAN REVIEW + CUSTOMER TEST" if research_ready else
                         "RESEARCH: corroborate problems and identify actual alternatives"),
            "commercially_validated":False,
            "constraints":"No web fetching, LLM generation, commercial proof, payments or deployment performed."}

def render(data, state):
    sources = data.get("sources", [])
    findings = data.get("findings", [])
    concepts = data.get("concepts", [])
    title = clean(data["subject"], 150)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    def lines(rows): return "\n".join(rows) + "\n"
    source_rows = ["- **["+s["id"]+"] "+clean(s.get("title"),120)+"** — "+s["url"]+
        " | "+s.get("review_status","unchecked")+" | "+clean(s.get("kind"),40) for s in sources]
    research = lines([
        "# Evidence Lab — " + title, "", "Generated UTC: "+stamp, "Market: "+clean(data["market"]),
        "**IMPORTANT:** source review is self-declared; this program has not fetched or verified any URLs.",
        "", "## Research questions", *("- "+clean(x) for x in data.get("research_questions",[]) if clean(x)),
        "", "## Source register", *(source_rows or ["No sources provided."]),
        "", "## Claim ledger",
        *("- **"+x["id"]+"** ["+x["classification"]+"] "+x["statement"]+
          " | sources: "+(", ".join(x["source_ids"]) or "none")+
          " | independently hosted manually checked links: "+str(x["manually_reviewed_domains"])
          for x in state["claim_ledger"]),
        "", "## Direct competitors / substitutes",
        *("- "+clean(x.get("name"))+" — "+clean(x.get("url"))+" | listed price: "+
          (clean(x.get("price")) or "UNKNOWN (do not assume free)")
          for x in data.get("competitors",[]) if clean(x.get("name"))),
        "", "## Critical unknowns",
        "- Search intent and market sizing are UNKNOWN unless separately evidenced.",
        "- Willingness to pay, conversion, retention and CAC are UNKNOWN unless tested.",
        "- Supplier pricing and integrations require fresh primary-source confirmation.",
        "", "Research gate: "+("READY FOR HUMAN REVIEW" if state["research_ready_for_human_review"] else "BLOCKED"),
        "This is NOT business validation."
    ])
    strategy = lines([
        "# Strategy Lab — " + title,"", "## Out-of-the-box innovation lenses (PROMPTS, NOT MARKET FACTS)",
        *("- **"+name+"**: "+description for name,description in IDEA_LENSES),
        "", "## Submitted concept hypotheses",
        *("- **"+clean(c.get("name"))+"** ("+c["id"]+") | target: "+clean(c.get("target_user"))+
          " | differentiation: "+clean(c.get("differentiation_hypothesis"))+
          " | test: "+clean(c.get("smallest_test"))+
          " | success threshold: "+clean(c.get("success_criterion"))+
          " | evidence refs: "+(", ".join(c.get("finding_ids",[])) or "NONE")
          for c in concepts),
        "", "## Concept validation gates",
        *("- "+x["id"]+": "+("READY TO DESIGN CUSTOMER TEST" if x["test_ready"] else "BLOCKED")+
          " | missing: "+(", ".join(x["missing"]) or "none") for x in state["concepts"]),
        "", "## Red-team checklist",
        "- Could the incumbent copy this in one sprint? What is the real defensibility?",
        "- Is the distinctive feature useful to the buyer or merely novel?",
        "- What existing workaround already solves it sufficiently?",
        "- Could differentiation increase onboarding, trust, support or regulatory costs?",
        "- What observable result would falsify this concept?",
        "", "NO ideas are ranked as commercially superior without measured tests."
    ])
    build = lines([
        "# Execution Plan — " + title, "",
        "## Decision state", "**"+state["next_gate"]+"**",
        "No autonomous build, publication or spending authorization.",
        "", "## Chronological gates and deliverables",
        *("### "+str(i)+". "+name.upper()+"\nGoal: "+desc+"\nDeliverable: "+
          {"select":"selection.json","research":"RESEARCH_BRIEF.md and primary-source evidence",
           "strategy":"STRATEGY_LAB.md with differentiated concepts and red-team critiques",
           "validate":"TEST_CARD.md and actual customer observations","spec":"SPEC.md, acceptance tests and decision record",
           "build":"tested MVP and test evidence","launch":"controlled pilot metrics","iterate":"weekly decision log"}[name]
          for i,(name,desc) in enumerate(STEPS,1)),
        "", "## Test design (preregister before outreach or launch)",
        "- Primary metric: actual paid commitment or measurable realized value.",
        "- Secondary metrics: activation, time-to-value, retention, support workload.",
        "- Set sample, threshold, stop condition, expiry and authorized cost ceiling BEFORE testing.",
        "- GO only after observed evidence; otherwise PIVOT or STOP.",
        "", "## Costs and permissions", "Budget: NOT APPROVED. All paid APIs, external account writes, outreach, publication, launch and deployment require explicit approval.",
        "Use a private repository for any business idea, sensitive dossier or proprietary strategy."
    ])
    progress = {"generated_at":stamp,"subject":title,
                "research_gate":state["research_ready_for_human_review"],
                "commercially_validated":False,
                "status":"RESEARCH_IN_PROGRESS" if not state["research_ready_for_human_review"] else "HUMAN_REVIEW_REQUIRED",
                "current_step":"research",
                "phases":[{"id":key,"name":desc,
                           "status":("complete" if key=="select" else "in_progress" if key=="research" else "blocked")}
                          for key,desc in STEPS],
                "blockers":([] if state["research_ready_for_human_review"] else
                             ["Two independently hosted manually reviewed sources supporting the same observed problem, plus a concrete alternative/competitor"]),
                "next_actions":["Read and manually verify each primary source",
                                "Record conflicting evidence and existing paid alternatives",
                                "Draft a falsifiable offer and customer-test card"],
                "approved_external_actions":[],"actual_revenue_eur":None,
                "costs_spent_eur":None,"outcome":"NOT TESTED"}
    return {"RESEARCH_BRIEF.md":research,"STRATEGY_LAB.md":strategy,
            "BUILD_PLAN.md":build,"PROGRESS.json":json.dumps(progress,indent=2,ensure_ascii=False)+"\n",
            "EVIDENCE_ASSESSMENT.json":json.dumps(state,indent=2,ensure_ascii=False)+"\n"}

def run(input_path, output_dir):
    data=validate(json.loads(Path(input_path).read_text(encoding="utf-8")))
    state=assess(data)
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    for filename,content in render(data,state).items():
        (output_dir/filename).write_text(content,encoding="utf-8")
    return state

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    state=run(args.input,args.output_dir)
    print(json.dumps({"output_dir":str(args.output_dir),"research_gate":state["research_ready_for_human_review"],
                      "concepts":len(state["concepts"]),"commercially_validated":False}))
if __name__=="__main__":main()
