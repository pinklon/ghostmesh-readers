"""Private Scout deep-source comparison panel. Explicitly separate work from identity."""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

def render(data):
    if data.get("schema")!="scout-deep-source-comparisons-v0" or any(data.get(k) is not False for k in ("publication_authorized","outreach_authorized")):raise ValueError("Private evidence required")
    esc=lambda x:escape(str(x),quote=True)
    pieces=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | Deep Source Reviews</title>',
    """<style>:root{color-scheme:dark;--bg:#101216;--fg:#f3f2f2;--dim:#b7b9c0;--red:#ef465c;--edge:#48494e}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,sans-serif}header,main,footer{padding:30px max(23px,calc((100vw - 1080px)/2))}header{border-bottom:1px solid var(--edge)}h1{font-size:clamp(36px,5vw,65px);letter-spacing:-.05em;line-height:1.1;margin:8px 0 15px}h2{font-size:29px;letter-spacing:-.03em;line-height:1.2}.eyebrow,h3{color:var(--red);font:750 12px ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase}.muted,footer{color:var(--dim)}article{border-top:2px solid var(--edge);padding:28px 0 35px}article:first-of-type{border-top-color:var(--red)}section{max-width:85ch}h3{margin:20px 0 6px}p{margin:8px 0 12px}a{color:var(--fg);text-underline-offset:4px;overflow-wrap:anywhere}a:hover{color:var(--red)}footer{border-top:1px solid var(--edge);font-size:12px}a:focus-visible{outline:2px solid var(--red)}</style>""",
    '</head><body><header><div class="eyebrow">GHOSTMESH / SCOUT · SOURCE INVESTIGATIONS</div><h1>What might actually change?</h1><p class="muted">Evidence-backed work comparisons. A promising idea is not a verified collaborator, tested integration, or permission to merge anything.</p></header><main>']
    ids=set()
    for x in data.get("assessments",[]):
        if x.get("id") in ids:raise ValueError("Duplicate assessment")
        ids.add(x.get("id"))
        if not all(x.get(k) for k in ("id","title","source_urls","source_observations","ghostmesh_problem","unexpected_connection","strongest_objection","disposition","small_test")):raise ValueError("Incomplete assessment")
        for url in x["source_urls"]:
            u=urlsplit(url)
            if u.scheme!="https" or u.username or u.password:raise ValueError("Invalid source URL")
        pieces.extend(['<article><div class="eyebrow">'+esc(x["disposition"])+'</div><h2>'+esc(x["title"])+'</h2>',
            '<p class="muted">Source: '+esc(x["source_version_note"])+'</p>',
            '<p>'+''.join('<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">Primary evidence '+str(i+1)+' ↗</a> &nbsp; ' for i,url in enumerate(x["source_urls"]))+'</p>',
            '<h3>Why this discovery is surprising</h3><p>'+esc(x["unexpected_connection"])+'</p>',
            '<h3>GhostMesh problem</h3><p>'+esc(x["ghostmesh_problem"])+'</p>',
            '<h3>What the source demonstrates or claims</h3>',
            ''.join('<p>'+esc(item)+'</p>' for item in x["source_observations"]),
            '<h3>Strongest objection</h3><p>'+esc(x["strongest_objection"])+'</p>',
            '<h3>Missing verification</h3>',
            ''.join('<p class="muted">'+esc(item)+'</p>' for item in x.get("missing_evidence",[])),
            '<h3>Smallest decisive test</h3><p>'+esc(x["small_test"])+'</p></article>'])
    pieces.append('</main><footer>Owner-private research only · No real-world identity verification · No deployment, publication or contact authority</footer></body></html>')
    return ''.join(pieces)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    a.out.write_text(render(json.loads(a.source.read_text(encoding="utf-8"))),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
