#!/usr/bin/env python3
"""Release candidate: offline, privacy-first venture dossier with fail-closed gates.

Never browses, installs skills, invokes paid APIs, contacts customers or deploys.
"""
import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from innovation_engine import evaluate as evaluate_innovation, markdown as innovation_markdown
from venture_studio import assess, render, validate, clean

MAX_BYTES=2_000_000
FILES={"RESEARCH_BRIEF.md","STRATEGY_LAB.md","BUILD_PLAN.md",
       "PROGRESS.json","EVIDENCE_ASSESSMENT.json","INNOVATION_DOSSIER.md",
       "INNOVATION_ASSESSMENT.json","RELEASE_MANIFEST.json"}

def load_json(path):
    path=Path(path)
    if not path.is_file() or path.stat().st_size>MAX_BYTES:
        raise ValueError("input must exist and be at most 2 MB")
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict):raise ValueError("input JSON must be object")
    return data

def build(selection,innovation=None):
    validate(selection)
    state=assess(selection)
    artifacts=render(selection,state)
    gate="RESEARCH_BLOCKED"
    if innovation is not None:
        ir=evaluate_innovation(innovation)
        if ir["subject"]!=selection["subject"]:
            raise ValueError("innovation subject mismatch")
        # Integrity: optional innovation claims must be referentially traceable
        # to the same selected subject. Input sources remain unverified.
        artifacts["INNOVATION_DOSSIER.md"]=innovation_markdown(ir)
        artifacts["INNOVATION_ASSESSMENT.json"]=json.dumps(ir,ensure_ascii=False,indent=2)+"\n"
        gate=("HUMAN_REVIEW_REQUIRED" if state["research_ready_for_human_review"] and
              ir["benchmark_complete"] else "RESEARCH_BLOCKED")
    elif state["research_ready_for_human_review"]:
        gate="HUMAN_REVIEW_REQUIRED"
    return artifacts,gate

def deliver(selection_path,output_dir,innovation_path=None,overwrite=False):
    selection=load_json(selection_path)
    innovation=load_json(innovation_path) if innovation_path is not None else None
    artifacts,gate=build(selection,innovation)
    output_dir=Path(output_dir)
    # Never overwrite existing business research or prior tracking by default.
    if output_dir.exists():
        if not output_dir.is_dir():raise ValueError("output path is not a directory")
        if any(output_dir.iterdir()):
            raise FileExistsError("output directory is nonempty; choose new path")
    else:
        output_dir.mkdir(parents=True,exist_ok=False)
    manifest={"schema_version":"1.0","generated_at":datetime.now(timezone.utc).isoformat(),
              "subject":clean(selection["subject"],150),
              "release_status":"OFFLINE_DOSSIER_GENERATED; NOT AUTONOMOUS RESEARCH OR COMMERCIAL VALIDATION",
              "gate":gate,"files":{},"approval_required_for":["outreach","payments","publishing","deployments","repository_visibility_changes"],
              "network_calls_performed":0,"costs_incurred_by_program_eur":0}
    for name,body in artifacts.items():
        manifest["files"][name]={"sha256":hashlib.sha256(body.encode("utf-8")).hexdigest(),"bytes":len(body.encode("utf-8"))}
    artifacts["RELEASE_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2)+"\n"
    # Create with exclusive mode. Existing files are never silently overwritten.
    created=[]
    try:
        for name,body in artifacts.items():
            p=output_dir/name
            with p.open("x",encoding="utf-8") as fp:fp.write(body)
            created.append(p)
    except Exception:
        for p in created:p.unlink(missing_ok=True)
        raise
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--selection",type=Path,required=True)
    p.add_argument("--innovation",type=Path)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(deliver(args.selection,args.output_dir,args.innovation),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
