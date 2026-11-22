"""Append persisted run/retry receipts to the existing private Scout History view."""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path

def render(html,run_reports,state):
    if "noindex,nofollow" not in html or "</main>" not in html:raise ValueError("Private history required")
    if state.get("schema")!="scout-persistent-ingestion-state-v0":raise ValueError("Unexpected ledger state")
    if state.get("outreach_authorized") is not False or state.get("publication_authorized") is not False:raise ValueError("Private only")
    if not run_reports:raise ValueError("Run receipts required")
    e=lambda value:escape(str(value),quote=True)
    out=['<section id="persistent-recovery" style="margin:30px auto;max-width:1080px;padding:23px;border:1px solid #555">',
         '<h2>Persisted ingest and retry history</h2><p>Offline recovery demonstration. Unsuccessful captures remain pending; successful retries clear them without advancing a timestamp cursor.</p>',
         '<p><strong>Saved runs:</strong> ',str(state["runs"]),' · <strong>Tracked source revisions:</strong> ',
         str(len(state["seen_keys"])),' · <strong>Pending retries:</strong> ',str(len(state["pending"])),'</p>']
    for report in run_reports:
        if report.get("schema")!="scout-persistent-ingestion-run-v0" or report.get("publication_authorized") is not False or report.get("outreach_authorized") is not False:
            raise ValueError("Invalid private run")
        out.extend(['<details><summary>Run ',str(report["run_number"]),': ',
          str(report["accepted"]),' accepted · ',str(report["deferred"]),' deferred · ',
          str(report["duplicate_revisions"]),' duplicate revisions</summary>'])
        for x in report["failure_receipts"]:
            out.extend(['<p>DEFERRED RETRY: ',e(x["url"]),' · ',e(x["error_code"]),
                        ' · attempts ',str(x["attempts"]),'</p>'])
        for x in report["source_receipts"]:
            out.extend(['<p>',e(x["state"]),': ',e(x["source_identity"]),
                        ' · ',e(x["revision"] or "UNVERIFIED"),
                        ' · person ',e(x["person_identity"]),'</p>'])
        out.append('</details>')
    out.extend(['<p>Failure statuses are recorded, not automatically retried. Source hashes witness captured bytes, not authenticity or identity.</p></section>'])
    return html.replace("</main>","".join(out)+"</main>",1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--history",required=True,type=Path)
    p.add_argument("--state",required=True,type=Path)
    p.add_argument("--run",action="append",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse overwrite")
    read=lambda p:json.loads(p.read_text(encoding="utf-8"))
    a.out.write_text(render(a.history.read_text(encoding="utf-8"),[read(path) for path in a.run],read(a.state)),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
