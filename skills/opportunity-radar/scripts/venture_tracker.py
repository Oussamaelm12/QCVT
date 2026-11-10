#!/usr/bin/env python3
"""Local, append-only auditable progress tracking; no integrations or side effects."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from venture_studio import STEPS,domain,clean

STAGES={stage for stage,_ in STEPS}
STATES={"planned","in_progress","blocked","completed","stopped"}

def add_event(path,stage,state,note,evidence_url=None):
    path=Path(path)
    data=json.loads(path.read_text(encoding="utf-8"))
    if stage not in STAGES or state not in STATES:raise ValueError("invalid stage/state")
    if not clean(note):raise ValueError("event note required")
    if evidence_url and not domain(evidence_url):raise ValueError("evidence_url must be HTTPS")
    if stage in {"validate","build","launch"} and state=="completed" and not evidence_url:
        raise ValueError("critical stage completion requires evidence URL")
    events=data.setdefault("events",[])
    if not isinstance(events,list):raise ValueError("events must be a list")
    event={"at":datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "stage":stage,"reported_state":state,
           "note":clean(note,1000),"evidence_url":evidence_url or None,
           "verification":"self-reported; not audited by software"}
    events.append(event)
    phases=data.get("phases",[])
    for phase in phases:
        if phase.get("id")==stage:
            phase["status"]=state
            break
    else:
        raise ValueError("unknown phase in progress file")
    data["updated_at"]=event["at"]
    data["last_reported_step"]=stage
    # Non-authoritative user updates never change revenue or commercial validation.
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return event

def summary(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    return {"subject":data.get("subject"),"updated_at":data.get("updated_at"),
            "reported_phases":[{"id":p.get("id"),"status":p.get("status")} for p in data.get("phases",[])],
            "reported_events":len(data.get("events",[])),
            "last_event":data.get("events",[])[-1] if data.get("events",[]) else None,
            "commercially_validated":data.get("commercially_validated",False),
            "actual_revenue_eur":data.get("actual_revenue_eur"),
            "warning":"Stage entries and linked evidence are self-reported, not source-verified. No independent financial audit."}

def main():
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest="command",required=True)
    record=sp.add_parser("record")
    record.add_argument("--progress",type=Path,required=True)
    record.add_argument("--stage",required=True,choices=sorted(STAGES))
    record.add_argument("--state",required=True,choices=sorted(STATES))
    record.add_argument("--note",required=True)
    record.add_argument("--evidence-url")
    report=sp.add_parser("status")
    report.add_argument("--progress",type=Path,required=True)
    args=p.parse_args()
    output=(add_event(args.progress,args.stage,args.state,args.note,args.evidence_url)
            if args.command=="record" else summary(args.progress))
    print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
