"""Append source-reviewed capability assessments to the existing private delta view.

Only README documentation has been inspected. Never upgrade metadata similarity
into proof of code correctness, originality, or collaborator identity.
"""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

REQUIRED=("id","source_url","observed_documentation","existing_ghostmesh",
          "specific_difference","transfer_question","strongest_objection",
          "minimum_test","status","source_review","runtime_verified","identity_verified")
def enrich(html, data):
    if data.get("schema")!="scout-source-reviewed-deltas-v0" or data.get("publication_authorized") is not False or data.get("outreach_authorized") is not False:
        raise ValueError("Research-only review required")
    if "noindex,nofollow" not in html or "</main>" not in html:
        raise ValueError("Invalid private destination")
    ids=set()
    e=lambda x:escape(str(x),quote=True)
    out=['<section id="source-reviewed-deltas" style="padding-top:32px;border-top:3px solid var(--accent)">',
         '<p class="kicker">SOURCE-REVIEWED / Public documentation</p>',
         '<h2>What actually differs?</h2>',
         '<p class="muted">These six cases were compared against public README documentation and an incomplete GhostMesh research baseline. No source code was executed; claimed behavior and transfer benefits remain unverified.</p>']
    for x in data.get("cases",[]):
        if any(k not in x for k in REQUIRED):raise ValueError("Missing source evidence")
        if x["id"] in ids:raise ValueError("Duplicate case")
        ids.add(x["id"])
        if x["runtime_verified"] is not False or x["identity_verified"] is not False:raise ValueError("Unverified status required")
        url=urlsplit(x["source_url"])
        if url.scheme!="https" or url.hostname!="github.com" or url.username or url.password:raise ValueError("Invalid link")
        if not isinstance(x["observed_documentation"],list) or not x["observed_documentation"]:raise ValueError("No documented features")
        out.extend(['<article><aside>',e(x["status"]),'<p>README REVIEWED</p><p>RUNTIME NOT VERIFIED</p></aside><section><h2>',
             e(x["id"].replace("-"," ").title()),'</h2><p><a target="_blank" rel="noopener noreferrer" href="',
             e(x["source_url"]),'">Inspect public source ↗</a></p><p><strong>Documented behavior:</strong> ',
             e("; ".join(x["observed_documentation"])),'</p><p><strong>GhostMesh today:</strong> ',
             e(x["existing_ghostmesh"]),'</p><p><strong>Potential distinction:</strong> ',
             e(x["specific_difference"]),'</p><p><strong>Discriminating question:</strong> ',
             e(x["transfer_question"]),'</p><p><strong>Strongest objection:</strong> ',
             e(x["strongest_objection"]),'</p><p><strong>Small test:</strong> ',
             e(x["minimum_test"]),'</p></section></article>'])
    out.append('</section>')
    return html.replace("</main>","".join(out)+"</main>",1)

def main():
    p=argparse.ArgumentParser()
    for key in ("html","review","out"):p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    a.out.write_text(enrich(a.html.read_text(encoding="utf-8"),
                            json.loads(a.review.read_text(encoding="utf-8"))),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
