"""Scout single-command, owner-private research run.

Explicit one-shot operation: collect or replay a frozen intake, run triage,
edition, reconciliation, and build an inspectable private HTML dashboard.
No scheduler, models, accounts, outreach or production publication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime,timezone
from pathlib import Path

from scout_signal_intake import run as collect
from scout_relevance_triage import triage
from scout_private_edition import edition
from scout_signal_reconcile import reconcile
from scout_multi_source_preview import render

def _json_bytes(obj):
    return (json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode("utf-8")

def _write(path,content):
    with path.open("xb") as f:
        f.write(content)

def build_run(intake,watch_catalog,previous=None):
    if intake.get("schema")!="scout-multisource-intake-v0":
        raise ValueError("Invalid intake")
    if not isinstance(intake.get("sampled_leads"),list):
        raise ValueError("Missing intake signals")
    for source in (intake,watch_catalog,previous):
        if source is not None and (source.get("publication_authorized") is not False or source.get("outreach_authorized") is not False):
            raise ValueError("Research-only authority required")
    if watch_catalog.get("schema")!="scout-watch-catalog-v0":
        raise ValueError("Invalid watch catalog")
    result_triage=triage(intake)
    result_edition=edition(intake,result_triage,watch_catalog)
    result_reconcile=reconcile(intake,previous)
    html=render(intake,result_triage,result_edition,result_reconcile)
    if "noindex,nofollow" not in html or "</html>" not in html:
        raise ValueError("Private workspace rendering failed")
    return {"intake.json":_json_bytes(intake),
            "triage.json":_json_bytes(result_triage),
            "edition.json":_json_bytes(result_edition),
            "reconciliation.json":_json_bytes(result_reconcile),
            "index.html":html.encode("utf-8")}

def commit_run(outputs,root,run_id,prior=None):
    if not run_id or not all(c.isascii() and (c.isalnum() or c in "-_") for c in run_id) or len(run_id)>64:
        raise ValueError("Invalid run identifier")
    root=Path(root)
    final=root/run_id
    if final.exists():raise FileExistsError("Run already exists; refusing overwrite")
    root.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix=".scout-staging-",dir=root))
    try:
        digests={}
        for filename,blob in outputs.items():
            if filename not in {"intake.json","triage.json","edition.json","reconciliation.json","index.html"}:
                raise ValueError("Unexpected generated output")
            _write(work/filename,blob)
            digests[filename]=hashlib.sha256(blob).hexdigest()
        if len(digests)!=5:raise ValueError("Incomplete run outputs")
        intake=json.loads(outputs["intake.json"])
        review=json.loads(outputs["edition.json"])
        receipt={"schema":"scout-integrated-run-v0","run_id":run_id,
           "captured_utc":intake.get("captured_utc"),"sources":intake.get("diagnostics",[]),
           "leads":len(intake["sampled_leads"]),"candidate_count":review["candidate_count"],
           "source_snapshot_origin":"ONE_SHOT_PUBLIC_COLLECTION_OR_EXPLICIT_OFFLINE_INPUT",
           "previous_snapshot_provided":prior is not None,
           "sha256":digests,
           "limitations":["Metadata only unless a separate content inspection is completed",
                          "No historical identity or trend inference","Not a production or continuously updated service"],
           "publication_authorized":False,"outreach_authorized":False}
        _write(work/"manifest.json",_json_bytes(receipt))
        os.rename(work,final)
        return receipt
    finally:
        if work.exists():
            import shutil
            shutil.rmtree(work)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-root",required=True,type=Path)
    p.add_argument("--run-id",required=True)
    p.add_argument("--catalog",required=True,type=Path)
    p.add_argument("--offline-intake",type=Path,help="Use frozen captured data; no network")
    p.add_argument("--previous",type=Path,help="Previous intact intake.json, read only")
    p.add_argument("--cap",type=int,default=8)
    a=p.parse_args()
    if (a.run_root/a.run_id).exists():raise SystemExit("Existing run ID; no overwrite")
    load=lambda path:json.loads(path.read_text(encoding="utf-8"))
    intake=load(a.offline_intake) if a.offline_intake else collect(cap=a.cap)
    previous=load(a.previous) if a.previous else None
    outputs=build_run(intake,load(a.catalog),previous)
    receipt=commit_run(outputs,a.run_root,a.run_id,a.previous)
    print(json.dumps({"run_dir":str(a.run_root/a.run_id),"leads":receipt["leads"],
                      "candidate_count":receipt["candidate_count"],"files":sorted(outputs)},indent=2))
if __name__=="__main__":main()
