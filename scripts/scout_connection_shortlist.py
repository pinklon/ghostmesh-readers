"""Render an owner-private, source-backed Scout connection-thesis review.

This is editorial evidence, not identification of collaborators or permission to
contact authors. Keep links and supporting claims tied to source-work records.
"""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

FIELDS=("id","title","source_url","source_kind","source_status","work_basis",
        "ghostmesh_problem","complementarity","counterevidence","experiment",
        "disposition","review_status")
VERDICTS={"INVESTIGATE","FOLLOW","NO_CONNECTION_JUSTIFIED"}

def validate(record):
    if record.get("schema")!="scout-connection-theses-v1":
        raise ValueError("Unexpected data schema")
    if record.get("publication_authorized") is not False or record.get("outreach_authorized") is not False:
        raise ValueError("Cannot publish or contact")
    if record.get("people_identity_verified") is not False:
        raise ValueError("Identity not established")
    seen=set()
    for item in record.get("theses",[]):
        if not all(isinstance(item.get(field),str) and item[field].strip() for field in FIELDS):
            raise ValueError("Incomplete evidence case")
        if item["id"] in seen:raise ValueError("Duplicate thesis ID")
        seen.add(item["id"])
        if item["disposition"] not in VERDICTS:raise ValueError("Invalid verdict")
        url=urlsplit(item["source_url"])
        if url.scheme!="https" or url.username or url.password:
            raise ValueError("Source must be clean HTTPS")
        if item["disposition"]=="NO_CONNECTION_JUSTIFIED" and not item["experiment"].lower().startswith("none"):
            raise ValueError("Negative control may not invent experiments")
    return record

def render(record):
    data=validate(record)
    esc=lambda s:escape(str(s),quote=True)
    out=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | Connection Theses</title>',
    """<style>:root{color-scheme:dark;--bg:#111317;--surface:#1b1d23;--ink:#f5f5f5;--muted:#b7bac1;--line:#41454e;--accent:#ee455d}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,-apple-system,sans-serif}header,main,footer{padding:28px max(24px,calc((100vw - 1120px)/2))}header{border-bottom:1px solid var(--line)}h1{font-size:clamp(38px,6vw,72px);line-height:1.07;letter-spacing:-.055em;margin:12px 0}h2{font-size:clamp(25px,3vw,37px);letter-spacing:-.04em;line-height:1.2;margin:4px 0 14px}h3{font-size:13px;color:var(--accent);letter-spacing:.12em;text-transform:uppercase;margin:24px 0 6px}p{max-width:80ch}.eyebrow{font:750 11px ui-monospace,monospace;letter-spacing:.14em;color:var(--accent)}.muted,footer{color:var(--muted)}.controls{display:flex;flex-wrap:wrap;gap:15px;padding:25px 0;border-bottom:1px solid var(--line)}input,select{padding:12px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;min-height:44px}input{flex:1;min-width:220px}select{min-width:200px}input:focus-visible,select:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:3px}.case{display:grid;grid-template-columns:190px 1fr;gap:30px;padding:35px 0;border-bottom:1px solid var(--line)}aside{color:var(--muted);font:700 11px/1.8 ui-monospace,monospace}.tag{border:1px solid var(--accent);color:var(--accent);padding:5px 8px;display:inline-block;margin-bottom:12px}.negative{opacity:.75}.case p{margin:8px 0 13px}a{color:inherit;text-underline-offset:4px;overflow-wrap:anywhere}a:hover{color:var(--accent)}footer{border-top:1px solid var(--line);font-size:12px}@media(max-width:700px){.case{grid-template-columns:1fr;gap:8px}}</style>""",
    '</head><body><header><div class="eyebrow">GHOSTMESH / SCOUT · PRIVATE EDITORIAL RESEARCH</div><h1>Unexpected connections.<br>Earned, not assumed.</h1><p class="muted">Source-linked proposals with specific GhostMesh questions, strongest objections, and discriminating experiments. Not a popularity chart or a contact list.</p></header><main><div class="controls"><input id="filter" type="search" placeholder="Search source, idea, problem or objection" aria-label="Filter theses"><select id="verdict" aria-label="Filter research disposition"><option value="ALL">All research dispositions</option><option value="INVESTIGATE">Investigate</option><option value="FOLLOW">Follow</option><option value="NO_CONNECTION_JUSTIFIED">No connection justified</option></select></div><p id="count" role="status"></p><div id="items">']
    for item in data["theses"]:
        search=" ".join(item[field] for field in FIELDS).lower()
        negative=item["disposition"]=="NO_CONNECTION_JUSTIFIED"
        out.extend(['<article class="case'+(' negative' if negative else '')+'" data-verdict="'+esc(item["disposition"])+'" data-search="'+esc(search)+'">',
            '<aside><div class="tag">'+esc(item["disposition"])+'</div><div>'+esc(item["source_kind"]).upper()+'</div><p>'+esc(item["review_status"])+'</p><p>'+esc(item["source_status"])+'</p></aside><section><h2>'+esc(item["title"])+'</h2>',
            '<p><a href="'+esc(item["source_url"])+'" target="_blank" rel="noopener noreferrer">Inspect original source ↗</a></p>',
            '<h3>What the work contributes</h3><p>'+esc(item["work_basis"])+'</p>',
            '<h3>Actual GhostMesh question</h3><p>'+esc(item["ghostmesh_problem"])+'</p>',
            '<h3>Possible complementarity, not a promise</h3><p>'+esc(item["complementarity"])+'</p>',
            '<h3>Strongest counterargument</h3><p>'+esc(item["counterevidence"])+'</p>',
            '<h3>Small discriminating experiment</h3><p>'+esc(item["experiment"])+'</p>',
            '</section></article>'])
    out.extend(['</div><p id="empty" hidden>No matching source-work cases.</p><p class="muted">These are work-based theses, not verified identities or invitations. Matching a paper to a problem does not establish authorship continuity, originality, technical reproducibility, or interest in collaboration.</p></main>',
        '<footer>Private research · No automatic outreach, identity resolution, publication, or production authorization</footer>',
        """<script>const cases=[...document.querySelectorAll('.case')],f=document.getElementById('filter'),v=document.getElementById('verdict');function update(){let count=0;for(const c of cases){let yes=c.dataset.search.includes(f.value.trim().toLowerCase())&&(v.value==='ALL'||c.dataset.verdict===v.value);c.hidden=!yes;if(yes)count++}document.getElementById('count').textContent=count+' evidence-linked theses shown';document.getElementById('empty').hidden=count!==0;}f.addEventListener('input',update);v.addEventListener('change',update);update();</script></body></html>"""])
    return "".join(out)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse to overwrite")
    html=render(json.loads(a.source.read_text(encoding="utf-8")))
    a.out.write_text(html,encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
