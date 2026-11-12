"""Append source-reviewed new discoveries to the existing private Scout theses view."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from html import escape
from urllib.parse import urlsplit

FIELDS=("id","title","article","repo","source_claim","ghostmesh_existing",
        "surprise","transfer","counterevidence","test","disposition","identity_status","runtime_status")
def render(html,review):
    if "noindex,nofollow" not in html or "</main>" not in html:
        raise ValueError("Private source page required")
    if (review.get("schema")!="scout-new-discovery-deep-review-v0" or
        review.get("publication_authorized") is not False or review.get("outreach_authorized") is not False):
        raise ValueError("Unapproved source assessment")
    cases=review.get("cases")
    if not isinstance(cases,list) or not cases:raise ValueError("No cases")
    e=lambda x:escape(str(x),quote=True)
    h=['<section id="unexpected-source-connections" style="margin-top:50px;padding-top:23px;border-top:3px solid var(--accent)">',
       '<div class="eyebrow">NEW / SOURCE-REVIEWED TRAILS</div><h2>What might change our thinking?</h2>',
       '<p class="muted">Three new public work trails examined against GhostMesh needs. Every proposed benefit remains unverified; no contributor identity or collaboration interest is established.</p>']
    ids=set()
    for item in cases:
        if not all(isinstance(item.get(k),str) and item[k].strip() for k in FIELDS):
            raise ValueError("Missing review evidence")
        if item["id"] in ids:raise ValueError("Duplicate case")
        ids.add(item["id"])
        if item["identity_status"]!="UNVERIFIED" or item["runtime_status"]!="NOT_RUN":
            raise ValueError("Unsupported identity or execution claims")
        for key in ("article","repo"):
            u=urlsplit(item[key])
            if u.scheme!="https" or u.username or u.password or u.hostname not in ("arxiv.org","dev.to","github.com"):
                raise ValueError("Unexpected external source")
        h.extend(['<article class="case"><aside><span class="tag">',e(item["disposition"]),
                  '</span><p>AUTHORSHIP NOT VERIFIED</p><p>CODE NOT RUN</p></aside><section><h2>',
                  e(item["title"]),'</h2><p><a target="_blank" rel="noopener noreferrer" href="',e(item["article"]),
                  '">Primary publication ↗</a> · <a target="_blank" rel="noopener noreferrer" href="',e(item["repo"]),
                  '">Public repository ↗</a></p>'])
        for title,key in (("Source-reported contribution","source_claim"),
                          ("GhostMesh already has","ghostmesh_existing"),
                          ("Why this is surprising","surprise"),
                          ("Potential transfer","transfer"),
                          ("Strongest objection","counterevidence"),
                          ("Small discriminating test","test")):
            h.extend(['<h3>',e(title),'</h3><p>',e(item[key]),'</p>'])
        h.append('</section></article>')
    h.append('</section>')
    return html.replace("</main>","".join(h)+"</main>",1)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for x in ("html","review","out"):p.add_argument("--"+x,type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("No overwrite")
    a.out.write_text(render(a.html.read_text(),json.loads(a.review.read_text())),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
