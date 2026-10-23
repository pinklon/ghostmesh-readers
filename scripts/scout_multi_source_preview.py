"""Build a local-only, browsable multi-lane Scout intelligence edition.

The edition displays captured signals with provenance and uncertainties.
No ranking, outreach, publication, or inferred social popularity.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from scout_visual_preview import CSS as BASE_CSS

CSS = BASE_CSS + """
.gm-wide{max-width:1180px;margin:auto;padding:40px 28px 80px}
.gm-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px solid var(--gm-border);border-bottom:1px solid var(--gm-border)}
.gm-stat{padding:21px 15px 21px 0}.gm-stat+.gm-stat{border-left:1px solid var(--gm-border);padding-left:18px}
.gm-stat b{font-size:36px;line-height:1;letter-spacing:-.06em}.gm-stat small{display:block;color:var(--gm-muted);font:700 11px/1.4 ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;margin-top:9px}
.gm-control{display:flex;gap:16px;flex-wrap:wrap;align-items:center;border-top:1px solid var(--gm-border);border-bottom:1px solid var(--gm-border);padding:18px 0;margin:32px 0}
.gm-control label{font:700 11px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.07em}
.gm-control select,.gm-control input{background:var(--gm-paper);color:var(--gm-ink);padding:10px 12px;border:1px solid var(--gm-border);min-height:44px;flex:1;min-width:150px;font:inherit}
.gm-list{display:grid;grid-template-columns:1fr}.gm-item{padding:22px 0;display:grid;grid-template-columns:170px 1fr;gap:30px;border-bottom:1px solid var(--gm-border)}
.gm-item h3{font-size:clamp(19px,2.5vw,27px);line-height:1.18;letter-spacing:-.035em;margin:0 0 11px}.gm-item h3 a{text-decoration:none}.gm-item h3 a:hover{text-decoration:underline;text-decoration-color:var(--gm-accent)}
.gm-item p{max-width:80ch;margin:6px 0;color:var(--gm-muted);font-size:14px}.gm-meta{font:750 10px/1.6 ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--gm-accent)}
.gm-label{display:inline-block;font:700 10px ui-monospace,monospace;letter-spacing:.06em;border:1px solid var(--gm-border);padding:5px 7px;margin-right:7px;text-transform:uppercase}
.gm-empty{padding:26px 0;color:var(--gm-muted)}.gm-section{margin-top:56px;padding-top:18px;border-top:2px solid var(--gm-accent)}
.gm-health{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.gm-health div{border-top:1px solid var(--gm-border);padding:12px 0;color:var(--gm-muted);font-size:13px}
@media(max-width:700px){.gm-stats{grid-template-columns:repeat(2,1fr)}.gm-stat:nth-child(3){border-left:0;padding-left:0}.gm-item{grid-template-columns:1fr;gap:5px}.gm-health{grid-template-columns:1fr}}
"""
LANES = ("attention","community","builder","research","engineering","code")
def render(intake: dict, triage: dict, edition: dict, reconcile: dict) -> str:
    if (intake.get("schema") != "scout-multisource-intake-v0"
        or triage.get("schema") != "scout-relevance-triage-v0"
        or edition.get("schema") != "scout-private-edition-v0"
        or reconcile.get("schema") != "scout-reconciliation-v0"):
        raise ValueError("Incorrect upstream schema")
    if any(obj.get("publication_authorized") is not False or obj.get("outreach_authorized") is not False
           for obj in (intake,triage,edition,reconcile)):
        raise ValueError("Any authority flag invalidates private edition")
    intake_urls={x["url"] for x in intake["sampled_leads"]}
    if any(x["url"] not in intake_urls for x in edition["candidates"]):
        raise ValueError("Unknown curated discovery")
    triage_by_url={x["url"]:x for x in triage["entries"]}
    # Display order is human review priority only, not a claim of objective significance.
    curated={x["url"]:x for x in edition["candidates"]}
    order={x["url"]:i for i,x in enumerate(edition["candidates"])}
    leads=sorted(intake["sampled_leads"],key=lambda x:(x["url"] not in curated,order.get(x["url"],100000),x["source"]))
    counts=Counter(x["lane"] for x in leads)
    e=lambda s:escape(str(s or ""),quote=True)
    h=["<!doctype html><html lang='en' data-theme='dark'><head><meta charset='utf-8'>",
       "<meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow,noarchive'>",
       "<title>Scout Intelligence | Private Edition</title><style>",CSS,"</style></head><body>",
       "<header class='gm-site-header'><div class='gm-site-header-inner'><a class='gm-site-brand' href='https://youtube.shareplane.malott.ai/'><strong>GHOST<em>MESH</em></strong><span>READERS / SCOUT</span></a>",
       "<nav class='gm-site-nav'><a href='https://youtube.shareplane.malott.ai/'>Readers</a><a href='#signals'>Intelligence</a><a href='#coverage'>Source coverage</a></nav>",
       "<button class='gm-theme' id='theme-toggle' type='button'>LIGHT / DARK</button></div></header>",
       "<main><section class='gm-hero'><div><p class='gm-kicker'>GhostMesh / Scout · Private intelligence edition</p>",
       "<h1>Watch the edges.<br>Keep the signal.</h1>",
       "<p>Engineering shifts, independent builders, technical conversations and research. Every item is an unreviewed lead until source evidence and editorial critique justify more.</p>",
       "</div><aside class='gm-summary'><p class='gm-kicker'>Current collection</p><strong>",str(len(leads))," public signals</strong>",
       "<small>Collection: ",e(intake.get("captured_utc")),"</small><p>Discovery only. No social accounts connected, popularity trajectory measured, or collaboration contact authorized.</p></aside></section>",
       "<section class='gm-wide' id='signals'><p class='gm-kicker'>Signals / First cross-source edition</p><h2>What entered view</h2>",
       "<div class='gm-stats'>",
       "<div class='gm-stat'><b>",str(len(leads)),"</b><small>Observed leads</small></div>",
       "<div class='gm-stat'><b>",str(len(curated)),"</b><small>Watch or topic match</small></div>",
       "<div class='gm-stat'><b>",str(reconcile.get("new_to_sample",0)),"</b><small>New to this sample</small></div>",
       "<div class='gm-stat'><b>",str(len({x['source'] for x in leads})),"</b><small>Named feed sources</small></div></div>",
       "<div class='gm-control'><label for='lane'>Signal stream</label><select id='lane'><option value='all'>All streams</option>"]
    for lane in LANES:
        h.extend(["<option value='",e(lane),"'>",e(lane.title())," (",str(counts[lane]),")</option>"])
    h.extend(["</select><label for='scope'>Research status</label><select id='scope'><option value='all'>All signals</option><option value='focus'>Topic-focused</option><option value='background'>Watched-feed background</option><option value='unmatched'>Other unreviewed</option></select>",
              "<label for='query'>Find in signals</label><input id='query' type='search' placeholder='Project, creator or topic' autocomplete='off'></div>",
              "<p id='visible-count' role='status' aria-live='polite'></p><div class='gm-list' id='lead-list'>"])
    for lead in leads:
        url=lead["url"]; candidate=curated.get(url); side=triage_by_url.get(url,{})
        scope=candidate.get("queue","BACKGROUND_WATCH") if candidate else "UNMATCHED"
        topics=side.get("topics",[])
        title=lead.get("title","Untitled")
        search=(title+" "+lead.get("description","")+" "+" ".join(topics)+" "+lead["source"]).lower()
        h.extend(["<article class='gm-item' data-lane='",e(lead["lane"] ),"' data-scope='",e(scope),"' data-search='",e(search),"'>",
                  "<aside><span class='gm-meta'>",e(lead["source"]),"</span><p>",e(lead["lane"].upper()),"</p><p>UNREVIEWED LEAD</p></aside><div>",
                  "<h3><a href='",e(url),"' rel='noopener noreferrer' target='_blank'>",e(title)," ↗</a></h3>",
                  "<p>",e(lead.get("description","")),"</p>"])
        for t in topics:
            h.extend(["<span class='gm-label'>",e(t.replace("-"," ")),"</span>"])
        if candidate:
            h.extend(["<p><strong>Queue:</strong> ",e(scope.replace("_"," ").title()),". GhostMesh relevance not yet independently verified.</p>"])
        h.append("</div></article>")
    h.extend(["</div><p class='gm-empty' id='empty' hidden>No signals match these filters.</p>",
              "<section id='coverage' class='gm-section'><p class='gm-kicker'>Collection health / visibility</p><h2>What Scout can actually see</h2><div class='gm-health'>"])
    for d in intake.get("diagnostics",[]):
        h.extend(["<div><strong>",e(d.get("source")),"</strong><p>",e(d.get("state"))," · ",e(d.get("items","no count"))," sampled</p></div>"])
    h.extend(["</div><p><strong>Not connected:</strong> X, Instagram, YouTube, Reddit and Bluesky are not represented by this collection. Gemini is not configured as a reviewer. Named-person watches are metadata checks, not verified identity tracking.</p>",
              "<p>Sampling can change as feed order changes; new-to-sample is not trend velocity. The source, title and metadata do not establish an article's claims, originality or GhostMesh benefit.</p>",
              "</section></section></main><footer class='gm-footer'><div class='gm-footer-inner'><strong>GHOSTMESH / SCOUT</strong><p>Context endures. Possibility evolves. Owner-private, no publication or outreach.</p></div></footer>",
              """<script>
const select=document.querySelector('#lane'),scope=document.querySelector('#scope'),query=document.querySelector('#query');
const cards=[...document.querySelectorAll('.gm-item')];
function update(){let count=0;const q=query.value.trim().toLowerCase();
for(const card of cards){const ok=(select.value==='all'||card.dataset.lane===select.value)&&
(scope.value==='all'||(scope.value==='focus'&&card.dataset.scope==='FOCUS_REVIEW')||
(scope.value==='background'&&card.dataset.scope==='BACKGROUND_WATCH')||
(scope.value==='unmatched'&&card.dataset.scope==='UNMATCHED'))&&card.dataset.search.includes(q);
card.hidden=!ok;if(ok)count++;}
document.querySelector('#visible-count').textContent=count+' signals shown';
document.querySelector('#empty').hidden=count!==0;}
[select,scope,query].forEach(x=>x.addEventListener('input',update));update();
document.querySelector('#theme-toggle').addEventListener('click',()=>{const x=document.documentElement;x.dataset.theme=x.dataset.theme==='light'?'dark':'light';});
</script></body></html>"""])
    return "".join(h)

def main():
    p=argparse.ArgumentParser()
    for field in ("intake","triage","edition","reconcile","out"):
        p.add_argument("--"+field,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists(): raise SystemExit("Refusing to overwrite preview")
    obj=lambda path:json.loads(path.read_text(encoding="utf-8"))
    a.out.write_text(render(obj(a.intake),obj(a.triage),obj(a.edition),obj(a.reconcile)),encoding="utf-8")
    print(a.out)

if __name__=="__main__":main()
