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
from scout_methodology_page import render_methodology, canonical_document
from scout_workspace import build as build_workspace, SECTIONS
from scout_relations import build as build_relations
from scout_relationship_preview import render as render_relationships
from scout_source_history import build as build_history
from scout_history_preview import render as render_history
from scout_run_evidence_queues import build as build_queues, render as render_queue
from scout_run_builder_questions import build as build_builder_questions, render as render_builder_questions
from scout_run_decisions import build as build_decisions, render as render_decisions

def _json_bytes(obj):
    return (json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode("utf-8")

def _write(path,content):
    with path.open("xb") as f:
        f.write(content)

def build_run(intake,watch_catalog,previous=None,historical_views=None):
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
    explanation=canonical_document()
    method_html=render_methodology(intake,explanation)
    html=html.replace("</main>", "<section class=\"gm-wide\"><h2>How signals enter Scout</h2><p>Read our sources, selection method, evidence limits and how to challenge a conclusion. <a href=\"methodology.html\" rel=\"noopener noreferrer\">Full methodology ↗</a></p></section></main>",1)
    outputs={"methodology.md":explanation.encode("utf-8"),
            "methodology.html":method_html.encode("utf-8"),
            "intake.json":_json_bytes(intake),
            "triage.json":_json_bytes(result_triage),
            "edition.json":_json_bytes(result_edition),
            "reconciliation.json":_json_bytes(result_reconcile),
            "index.html":html.encode("utf-8")}
    # All ten panels are generated from the run; old preview files are not required.
    # Reject old preview inputs to avoid accidentally treating them as current.
    if historical_views is not None:
        raise ValueError("Legacy HTML inputs are no longer accepted; all panels are generated")
    views={"discovery":html}
    views["history"]=("<!doctype html><html><head><meta name=\"robots\" "
        "content=\"noindex,nofollow,noarchive\"></head><body><main>"
        "<h1>History begins with this collection</h1>"
        "<p>No earlier source snapshot was supplied. This is not a revision history.</p>"
        "</main></body></html>")
    # Relationships are derived from this run, not copied from a prior snapshot.
    relations=build_relations(intake,result_triage,result_reconcile)
    views["relationships"]=render_relationships(relations)
    outputs["relations.json"]=_json_bytes(relations)
    # History needs at least two chronological snapshots. If unavailable,
    # keep the previous view labeled historical rather than invent one.
    if previous is not None:
        previous_triage=triage(previous)
        if previous["captured_utc"]<intake["captured_utc"]:
            source_history=build_history([(previous,previous_triage),(intake,result_triage)])
            views["history"]=render_history(source_history,relations)
            outputs["history.json"]=_json_bytes(source_history)
    queues=build_queues(intake,result_triage)
    views["claims"]=render_queue(queues,"claims")
    views["trails"]=render_queue(queues,"works")
    outputs["evidence_queues.json"]=_json_bytes(queues)
    builder_questions=build_builder_questions(intake,result_triage)
    views["people"]=render_builder_questions(builder_questions,"people")
    views["theses"]=render_builder_questions(builder_questions,"questions")
    outputs["builder_questions.json"]=_json_bytes(builder_questions)
    audit=build_decisions(intake,result_triage,result_edition,result_reconcile)
    views["replay"]=render_decisions(audit,"replay")
    views["differences"]=render_decisions(audit,"differences")
    outputs["decision_audit.json"]=_json_bytes(audit)
    # Source-deep review requires separate primary-source inspections. A normal\n    # one-shot intake cannot manufacture that evidence from feed metadata.\n    views["reviews"]=("<!doctype html><html><head><meta name=\\"robots\\" "+\n        "content=\\"noindex,nofollow,noarchive\\"></head><body><main>"+\n        "<h1>Source reviews require separate inspection</h1>"+\n        "<p>This collection contains public metadata, not independently read primary sources. "+\n        "No deep-review conclusions are available in this run.</p>"+\n        "</main></body></html>")\n    workspace=build_workspace(views)
    refreshed=["Discovery","Relationships","Claims (unverified queue)","Public work (observed links)","People (unverified handles)","Connection questions (unassessed)","Selection decisions (metadata only)","Capability questions (not measured)"]+ (["History"] if "history.json" in outputs else [])
    pinned=[]
    from html import escape
    note="Run-bound: "+", ".join(refreshed)+". "+("History rebuilt from two snapshots. " if "history.json" in outputs else "History awaiting an earlier snapshot. ")+"No panels depend on historical HTML files. "
    banner="<div role=\"status\" style=\"padding:12px 24px;background:#292126;color:#ffe1e5;border-bottom:1px solid #e83b52\">"+escape(note)+"<a style=\"color:#ffc4d0\" href=\"methodology.html\">How Scout collects signals ↗</a></div>"
    workspace=workspace.replace("</header>", "</header>"+banner,1)
    outputs["workspace.html"]=workspace.encode("utf-8")
    return outputs

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
            if filename not in {"intake.json","triage.json","edition.json","reconciliation.json","index.html","methodology.md","methodology.html","workspace.html","relations.json","history.json","evidence_queues.json","builder_questions.json","decision_audit.json"}:
                raise ValueError("Unexpected generated output")
            _write(work/filename,blob)
            digests[filename]=hashlib.sha256(blob).hexdigest()
        base={"intake.json","triage.json","edition.json","reconciliation.json",
              "index.html","methodology.md","methodology.html"}
        extended={"workspace.html","relations.json","evidence_queues.json",
                  "builder_questions.json","decision_audit.json"}
        allowed=(base,base|extended,base|extended|{"history.json"})
        if set(digests) not in allowed:
            raise ValueError("Incomplete or unexpected run outputs")
        intake=json.loads(outputs["intake.json"])
        review=json.loads(outputs["edition.json"])
        receipt={"schema":"scout-integrated-run-v0","run_id":run_id,
           "captured_utc":intake.get("captured_utc"),"sources":intake.get("diagnostics",[]),
           "leads":len(intake["sampled_leads"]),"candidate_count":review["candidate_count"],
           "source_snapshot_origin":"ONE_SHOT_PUBLIC_COLLECTION_OR_EXPLICIT_OFFLINE_INPUT",
           "previous_snapshot_provided":prior is not None,
           "workspace_view_status":{"discovery":"CURRENT_RUN","relationships":"CURRENT_RUN" if "relations.json" in outputs else "NOT_INCLUDED",
               "history":"TWO_SNAPSHOT_REBUILT" if "history.json" in outputs else "AWAITING_PRIOR_SNAPSHOT",
               "claims":"UNVERIFIED_CURRENT_RUN_QUEUE" if "evidence_queues.json" in outputs else "NOT_INCLUDED",
               "trails":"OBSERVED_LINKS_NOT_EXPANDED" if "evidence_queues.json" in outputs else "NOT_INCLUDED",
               "people":"UNVERIFIED_CURRENT_RUN_HANDLES" if "builder_questions.json" in outputs else "NOT_INCLUDED",
               "theses":"UNASSESSED_CURRENT_RUN_QUESTIONS" if "builder_questions.json" in outputs else "NOT_INCLUDED",
               "replay":"CURRENT_RUN_SELECTION_RECEIPTS" if "decision_audit.json" in outputs else "NOT_INCLUDED",
               "differences":"NOT_MEASURED_CURRENT_RUN_QUESTIONS" if "decision_audit.json" in outputs else "NOT_INCLUDED",\n               "reviews":"REQUIRES_SEPARATE_PRIMARY_SOURCE_REVIEW",
               "remaining_views":"NONE" if "decision_audit.json" in outputs else "PINNED_HISTORICAL" if "workspace.html" in outputs else "NOT_INCLUDED"},
           "methodology":"methodology.html",
           "methodology_source":"methodology.md",
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
