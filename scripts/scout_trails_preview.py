"""Render privately collected public-work trails, highlighting source-derived clues.

Highlight flags are editorial reading suggestions, NOT validated collaborator
quality, identity matches, or production recommendations.
"""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

TOPICS={
 "review-workflows":("code review","pull requests","background agents","patchnotes"),
 "retrieval-epistemics":("retrieval","rag","entity resolution","question answering","annotators","evaluation"),
 "agent-memory":("memory","mem0","meeting skills"),
 "change-observation":("website","alerts","changes","monitor"),
}
def annotate(data):
    if data.get("schema")!="scout-public-contribution-trails-v0":
        raise ValueError("Unexpected research source")
    if any(data.get(k) is not False for k in ("publication_authorized","outreach_authorized","identity_verified")):
        raise ValueError("No permissions or person identity verification")
    results=[]
    for item in data.get("trails",[]):
        if item.get("contact_authorized") is not False or item.get("same_real_person_confirmed") is not False:
            raise ValueError("Invalid authority")
        u=urlsplit(item.get("work_url",""))
        if u.scheme!="https" or u.username or u.password:raise ValueError("Invalid public link")
        haystack=" ".join([item.get("work_title",""),item.get("description","")]).lower()
        signals={topic:[w for w in words if w in haystack] for topic,words in TOPICS.items()}
        signals={k:v for k,v in signals.items() if v}
        results.append({**item,"topic_matches":signals,
            "review_status":"WORK_METADATA_CANDIDATE" if signals else "NO_TOPIC_MATCH",
            "originality":"NOT_ASSESSED","personal_identity":"NOT_VERIFIED"})
    return {"schema":"scout-public-trail-review-v0","items":results,
            "topic_matches":sum(bool(x["topic_matches"]) for x in results),
            "outreach_authorized":False,"publication_authorized":False}

def render(data):
    validated=annotate(data)
    esc=lambda x:escape(str(x or ""),quote=True)
    html=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | Public Work Trails</title>',
    """<style>:root{color-scheme:dark;--bg:#101216;--ink:#f3f3f5;--muted:#b7bbc4;--accent:#ef4058;--line:#474a52;--paper:#1c1f25}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,-apple-system,sans-serif}header,main,footer{padding:30px max(24px,calc((100vw - 1120px)/2))}header{border-bottom:1px solid var(--line)}h1{font-size:clamp(40px,6vw,70px);letter-spacing:-.06em;line-height:1.03;margin:10px 0 20px}h2{font-size:clamp(22px,3vw,34px);letter-spacing:-.035em;line-height:1.15}p{max-width:78ch}a{color:inherit;text-underline-offset:4px;overflow-wrap:anywhere}a:hover{color:var(--accent)}.kicker{font:700 11px ui-monospace,monospace;letter-spacing:.14em;color:var(--accent)}.muted,footer{color:var(--muted)}.filters{display:flex;flex-wrap:wrap;gap:12px;margin:22px 0;padding:19px 0;border-bottom:1px solid var(--line)}input,select{background:var(--paper);color:var(--ink);border:1px solid var(--line);padding:11px;min-height:44px;font:inherit}input{flex:1;min-width:230px}article{padding:27px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:200px 1fr;gap:22px}article p{margin:7px 0}.aside{font:700 11px/1.8 ui-monospace,monospace;color:var(--muted)}.signal{color:var(--accent)}footer{border-top:1px solid var(--line);font-size:12px}@media(max-width:720px){article{grid-template-columns:1fr}}</style>""",
    '</head><body><header><div class="kicker">GHOSTMESH / SCOUT · PUBLIC WORK TRACING</div><h1>Follow a contribution.<br>Find another.</h1><p class="muted">Additional papers and repositories discovered from six starting attributions. Shared names are not verified people. Repository ownership proves account continuity only.</p></header><main><div class="filters"><input id="query" type="search" placeholder="Search work, source, account or topic" aria-label="Search trails"><select id="kind" aria-label="Source type"><option value="all">All source trails</option><option value="arxiv_exact_byline_match">ArXiv byline match</option><option value="github_same_account_repository">GitHub account repository</option></select></div><p id="count" role="status"></p>']
    for item in validated["items"]:
        desc=item.get("description","")
        topics=", ".join(item["topic_matches"])
        search=(item["label"]+" "+item["work_title"]+" "+desc+" "+topics).lower()
        html.extend(['<article data-kind="'+esc(item["kind"])+'" data-search="'+esc(search)+'"><aside class="aside">',
            esc(item["label"]),'<p>'+esc(item["kind"].replace("_"," "))+'</p><p>'+esc(item["review_status"])+'</p></aside><section><h2>',
            esc(item["work_title"]),'</h2><p><a href="'+esc(item["work_url"])+'" target="_blank" rel="noopener noreferrer">Inspect public work ↗</a></p>',
            '<p class="muted">Discovered from: <a href="'+esc(item["origin_work"])+'" target="_blank" rel="noopener noreferrer">'+esc(item["origin_work"])+'</a></p>',
            '<p>'+esc(item["support"])+'</p>',
            '<p class="muted">'+esc(desc)+'</p>',
            '<p class="signal">Possible topic links: '+esc(topics or "None in metadata")+'</p>',
            '<p class="muted">Independent technical review and contributor identity verification: NOT DONE. Outreach: NOT AUTHORIZED.</p></section></article>'])
    html.extend(['<p id="empty" hidden>No matching trails.</p><p class="muted">Metadata matches are prompts to read original work. No automated conclusions about originality, capability, affiliation or collaboration intent.</p></main><footer>Owner-private evidence · No verified real-world person merge · No publication or outreach authority</footer>',
    """<script>const items=[...document.querySelectorAll('article')],q=document.getElementById('query'),k=document.getElementById('kind');function update(){let n=0;for(const a of items){let ok=a.dataset.search.includes(q.value.trim().toLowerCase())&&(k.value==='all'||a.dataset.kind===k.value);a.hidden=!ok;if(ok)n++}document.getElementById('count').textContent=n+' additional public work links';document.getElementById('empty').hidden=n>0}q.addEventListener('input',update);k.addEventListener('change',update);update();</script></body></html>"""])
    return "".join(html)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ("source","out"):p.add_argument("--"+field,type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse overwrite")
    a.out.write_text(render(json.loads(a.source.read_text(encoding="utf-8"))),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
