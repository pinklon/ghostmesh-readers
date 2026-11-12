"""Build conservative public-work contributor profiles and a private directory.

An identical name across papers is a label collision, not resolved identity.
"""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path

def profiles(data):
    if data.get("schema")!="scout-work-first-discovery-v0":
        raise ValueError("Unexpected attribution input")
    if data.get("publication_authorized") is not False or data.get("outreach_authorized") is not False:
        raise ValueError("Private research only")
    records=[]
    seen=set()
    for item in data.get("entries",[]):
        for field in ("id","kind","label","work_url","basis"):
            if not isinstance(item.get(field),str) or not item[field].strip():
                raise ValueError("Incomplete attribution")
        if item.get("identity_verified") is not False or item.get("contact_authorized") is not False:
            raise ValueError("Unexpected identity or contact authority")
        if not item["work_url"].startswith("https://"):raise ValueError("HTTPS work required")
        if item["id"] in seen:raise ValueError("Duplicate attribution")
        seen.add(item["id"])
        records.append({"id":item["id"],"display_label":item["label"],
          "kind":item["kind"],"source_work":item["work_url"],
          "work_title":item.get("work_title") or "Repository contribution",
          "account_url":item.get("account_url"),"basis":item["basis"],
          "identity_verified":False,"same_named_person_merge":False,
          "ghostmesh_complementarity":"UNASSESSED","connection_thesis":"NOT_WRITTEN",
          "originality":"UNASSESSED","contact_authorized":False})
    return {"schema":"scout-private-work-profiles-v0","profiles":records,"coverage":data.get("coverage",[]),
            "limits":["Each row is a work attribution, not a unique real-world individual",
                      "Equal author names are not merged without independent disambiguation",
                      "Contributor endpoint does not establish project governance or expertise",
                      "No inferred collaboration or outreach permission"],
            "publication_authorized":False,"outreach_authorized":False}

def render(data):
    if data.get("schema")!="scout-private-work-profiles-v0" or data.get("publication_authorized") is not False or data.get("outreach_authorized") is not False:
        raise ValueError("Invalid private profile data")
    e=lambda v:escape(str(v or ""),quote=True)
    h=['<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | People and Builders</title>',
    """<style>:root{color-scheme:dark;--bg:#101215;--paper:#181c21;--ink:#f4f4f5;--muted:#b6b8bd;--accent:#e94455;--line:#454a53}html[data-theme=light]{color-scheme:light;--bg:#fbfaf8;--paper:white;--ink:#1d1e20;--muted:#555a63;--accent:#c41732;--line:#d1d3d6}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,sans-serif}header,main,footer{padding:35px max(24px,calc((100vw - 1100px)/2))}.kicker{color:var(--accent);font:750 11px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.16em}h1{font-size:clamp(40px,5.8vw,74px);line-height:1.04;letter-spacing:-.06em;margin:13px 0 18px}header{border-bottom:1px solid var(--line)}header p{color:var(--muted);max-width:67ch}input,select,button{background:var(--paper);color:var(--ink);border:1px solid var(--line);padding:11px;font:inherit;min-height:44px}button{cursor:pointer}a{color:inherit;overflow-wrap:anywhere;text-underline-offset:4px}a:hover{color:var(--accent)}a:focus-visible,input:focus-visible,select:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:3px}.filters{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:22px 0;padding:22px 0;border-block:1px solid var(--line)}label{display:grid;gap:7px;font:700 11px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}article{display:grid;grid-template-columns:190px 1fr;gap:35px;border-top:1px solid var(--line);padding:28px 0}article h2{font-size:clamp(23px,2.8vw,31px);letter-spacing:-.035em;margin:0 0 12px;line-height:1.2}article p{font-size:14px;color:var(--muted);margin:8px 0}.side{font:700 11px ui-monospace,monospace;color:var(--accent);text-transform:uppercase}.note{border-top:2px solid var(--accent);margin-top:35px;padding-top:20px;color:var(--muted)}footer{border-top:1px solid var(--line);color:var(--muted);font-size:12px}@media(max-width:720px){.filters,article{grid-template-columns:1fr}}</style>""",
    '</head><body><header><p class="kicker">GHOSTMESH / SCOUT · Work-first discovery</p><h1>Follow the work.<br>Find the minds.</h1>',
    '<p>',str(len(data["profiles"])),' public work-attribution records. These are not verified unique people, social relationships, or recommendations to contact anyone.</p>',
    '<button id="theme" type="button">LIGHT / DARK</button></header><main><div class="filters"><label>Attribution type<select id="kind"><option value="all">All public work</option><option value="public_author_name">Research author names</option><option value="github_account_handle">GitHub account handles</option></select></label><label>Search names or work<input id="query" type="search" placeholder="Researcher, paper, project"></label></div><p id="count" role="status"></p><div id="profiles">']
    for p in data["profiles"]:
        if p["identity_verified"] is not False or p["contact_authorized"] is not False:
            raise ValueError("Invalid profile identity/contact status")
        search=(p["display_label"]+" "+p["work_title"]+" "+p["source_work"]).lower()
        h.extend(['<article data-kind="',e(p["kind"]),'" data-search="',e(search),'"><aside class="side">',
          e(p["kind"].replace("_"," ")),'<p>Identity unverified</p></aside><section><h2>',e(p["display_label"]),'</h2>',
          '<p><strong>Discovered through:</strong> <a href="',e(p["source_work"]),'" target="_blank" rel="noopener noreferrer">',e(p["work_title"]),' ↗</a></p>',
          '<p><strong>Attribution basis:</strong> ',e(p["basis"]),'</p>',
          '<p><strong>GhostMesh complementarity:</strong> NOT ASSESSED</p>',
          '<p><strong>Outreach:</strong> NOT AUTHORIZED</p></section></article>'])
    h.extend(['</div><p id="empty" hidden>No matching attributions.</p><section class="note"><p class="kicker">Evidence discipline</p><p>Names are not resolved across publications. A contributor may have made minor edits. This is a discovery surface, not an identity database or social graph.</p></section></main><footer>GHOSTMESH / SCOUT · Owner-private research · No publication or outreach</footer>',
    """<script>const kind=document.querySelector('#kind'),query=document.querySelector('#query'),items=[...document.querySelectorAll('article')];function update(){let n=0;for(const x of items){let visible=(kind.value==='all'||x.dataset.kind===kind.value)&&x.dataset.search.includes(query.value.trim().toLowerCase());x.hidden=!visible;if(visible)n++;}document.querySelector('#count').textContent=n+' work attributions shown';document.querySelector('#empty').hidden=n>0;}kind.addEventListener('change',update);query.addEventListener('input',update);update();document.querySelector('#theme').addEventListener('click',()=>{const r=document.documentElement;r.dataset.theme=r.dataset.theme==='light'?'dark':'light';});</script></body></html>"""])
    return "".join(h)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--html",required=True,type=Path)
    a=parser.parse_args()
    if a.out.exists() or a.html.exists():raise SystemExit("Refusing overwrite")
    data=profiles(json.loads(a.source.read_text(encoding="utf-8")))
    a.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    a.html.write_text(render(data),encoding="utf-8")
    print(json.dumps({"attributions":len(data["profiles"]),"output":str(a.html)}))
if __name__=="__main__": main()
