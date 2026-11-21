"""Owner-private Scout capability-delta review page, with caveats kept visible."""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path

def render(data):
    if data.get("schema")!="scout-capability-delta-triage-v0" or data.get("publication_authorized") is not False or data.get("outreach_authorized") is not False:
        raise ValueError("Private research only")
    h=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | Capability Differences</title>',
    """<style>:root{color-scheme:dark;--bg:#111317;--ink:#f4f4f5;--mute:#b4b7bf;--accent:#eb475b;--line:#41464f;--surface:#1b1f24}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 system-ui,sans-serif}header,main,footer{padding:30px max(20px,calc((100vw - 1120px)/2))}header{border-bottom:1px solid var(--line)}h1{font-size:clamp(37px,6vw,72px);letter-spacing:-.06em;line-height:1.02}h2{font-size:clamp(24px,3vw,34px);letter-spacing:-.04em;line-height:1.17}.kicker{color:var(--accent);font:750 11px ui-monospace,monospace;letter-spacing:.15em;text-transform:uppercase}.muted,footer{color:var(--mute)}a{color:inherit;text-underline-offset:4px;overflow-wrap:anywhere}a:hover{color:var(--accent)}article{display:grid;grid-template-columns:200px 1fr;gap:25px;border-top:1px solid var(--line);padding:27px 0}aside{font:700 11px ui-monospace,monospace;color:var(--accent);overflow-wrap:anywhere}.pair{background:var(--surface);border-left:2px solid var(--accent);padding:18px;margin-top:14px}.pair p{margin:8px 0}.filters{display:flex;flex-wrap:wrap;gap:12px;margin:18px 0}input,select{padding:11px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;min-height:44px}input{flex:1;min-width:220px}footer{border-top:1px solid var(--line);font-size:12px}@media(max-width:700px){article{grid-template-columns:1fr}}</style>""",
    '</head><body><header><p class="kicker">GHOSTMESH / SCOUT · CAPABILITY COMPARISON</p><h1>What is genuinely<br>different?</h1><p class="muted">Public work metadata compared against a documented, incomplete GhostMesh baseline. Keyword matches suggest research questions, never establish missing functionality, originality, or collaborator value.</p></header><main><p>',
    str(data["total_trails"]),' trails reviewed · ',str(data["trails_with_potential_delta"]),' potential matches · ',str(data["potential_delta_links"]),' possible topic links.</p>',
    '<div class="filters"><input id="q" type="search" aria-label="Search capability comparisons" placeholder="Search project, problem, objection"><select id="kind" aria-label="Filter evidence"><option value="all">All work</option><option value="candidate">Possible difference</option><option value="no_evidence">No metadata evidence</option></select></div><p id="count" role="status"></p>']
    e=lambda x:escape(str(x or ""),quote=True)
    for item in data["rows"]:
        if item.get("identity_verified") is not False or item.get("outreach_authorized") is not False:raise ValueError("Cannot validate identity")
        filtered="candidate" if item["candidates"] else "no_evidence"
        search=" ".join([item.get("work_title",""),item.get("attribution","")]+[c["possible_gap_to_test"] for c in item["candidates"]]).lower()
        h.extend(['<article data-kind="'+filtered+'" data-search="'+e(search)+'"><aside>'+e(item["attribution"])+'<p>'+e(item["trail_kind"].replace("_"," "))+'</p><p>'+e(item["status"])+'</p></aside><section><h2>'+e(item["work_title"])+'</h2>',
         '<p><a href="'+e(item["work_url"])+'" target="_blank" rel="noopener noreferrer">Source work ↗</a></p>'])
        if not item["candidates"]:h.append('<p class="muted">No relevant metadata vocabulary matched. This is not a negative technical review.</p>')
        for c in item["candidates"]:
            h.extend(['<div class="pair"><p class="kicker">',e(c["capability"]),'</p>',
                '<p><strong>We already have:</strong> ',e(c["existing_ghostmesh_baseline"]),'</p>',
                '<p><strong>What remains unmeasured:</strong> ',e(c["possible_gap_to_test"]),'</p>',
                '<p><strong>What to check:</strong> ',e(c["discriminating_question"]),'</p>',
                '<p><strong>Counterargument:</strong> ',e(c["strongest_objection"]),'</p>',
                '<p class="muted">Observed terms: ',e(", ".join(c["matched_metadata_terms"])),'. Novelty unassessed. Source review required.</p></div>'])
        h.append('</section></article>')
    h.extend(['</main><footer>Private research · Capability absence not established · No external contact, public release, or production authority</footer>',
    """<script>const q=document.getElementById('q'),k=document.getElementById('kind'),items=[...document.querySelectorAll('article')];function update(){let n=0;for(const x of items){const yes=x.dataset.search.includes(q.value.trim().toLowerCase())&&(k.value==='all'||x.dataset.kind===k.value);x.hidden=!yes;if(yes)n++;}document.getElementById('count').textContent=n+' public work records shown';}q.addEventListener('input',update);k.addEventListener('change',update);update();</script></body></html>"""])
    return "".join(h)
def main():
    p=argparse.ArgumentParser()
    for k in ("source","out"):p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse overwrite")
    a.out.write_text(render(json.loads(a.source.read_text(encoding="utf-8"))),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
