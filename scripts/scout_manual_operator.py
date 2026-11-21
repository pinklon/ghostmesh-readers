"""Manually run Scout once, automatically linking the last verified private run.

Research-only operator entrypoint. No timer, cron, outbound notifications,
publication, SSH transfer, or automatic deletion.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from scout_private_archive import inventory,verify_run
from scout_integrated_run import build_run,commit_run
from scout_signal_intake import run as collect

def latest_verified(root):
    root=Path(root)
    if not root.exists():return None
    listing=inventory(root)
    valid=[row for row in listing["runs"] if row["integrity"]=="VERIFIED"]
    if any(row["integrity"]!="VERIFIED" for row in listing["runs"]):
        raise ValueError("Existing unverified run requires operator review")
    if not valid:return None
    ordered=sorted(valid,key=lambda row:(row.get("captured_utc") or "",row["run_id"]))
    candidate=root/ordered[-1]["run_id"]
    verify_run(candidate)
    return candidate

def run_once(root,run_id,catalog,*,intake=None,cap=8):
    root=Path(root)
    previous_path=latest_verified(root)
    previous=json.loads((previous_path/"intake.json").read_text(encoding="utf-8")) if previous_path else None
    if intake is None:
        if not 1<=cap<=15:raise ValueError("Invalid cap")
        intake=collect(cap=cap)
    if previous and intake.get("captured_utc","")<=previous.get("captured_utc",""):
        raise ValueError("New capture must be newer than last verified run")
    outputs=build_run(intake,catalog,previous)
    manifest=commit_run(outputs,root,run_id,previous_path)
    return {"run_path":str(root/run_id),"previous_run":previous_path.name if previous_path else None,
        "leads":manifest["leads"],"reading_candidates":manifest["candidate_count"],
        "history_status":manifest["workspace_view_status"]["history"],
        "source_errors":sum(d.get("state")=="ERROR" for d in manifest["sources"]),
        "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--run-id",required=True)
    p.add_argument("--catalog",required=True,type=Path)
    p.add_argument("--cap",type=int,default=8)
    p.add_argument("--offline-intake",type=Path,help="Explicit captured input instead of public network access")
    a=p.parse_args()
    if (a.root/a.run_id).exists():raise SystemExit("Refusing overwrite")
    catalog=json.loads(a.catalog.read_text(encoding="utf-8"))
    intake=json.loads(a.offline_intake.read_text(encoding="utf-8")) if a.offline_intake else None
    print(json.dumps(run_once(a.root,a.run_id,catalog,intake=intake,cap=a.cap),indent=2))
if __name__=="__main__":main()
