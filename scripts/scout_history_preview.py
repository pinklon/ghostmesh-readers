"""Local-only GhostMesh Scout relationship timeline derived from two source samples."""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path

CSS="""
:root{color-scheme:dark;--bg:#111316;--ink:#f2f3f4;--muted:#bac0c8;--line:#41474f;--accent:#eb4054;--paper:#1a1d22}
html[data-theme=light]{color-scheme:light;--bg:#fcfaf8;--ink:#191c20;--muted:#505762;--line:#d5d5d5;--accent:#bb1733;--paper:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}
a{color:inherit;text-underline-offset:4px}a:hover{color:var(--accent)}
button,select,input{font:inherit;color:var(--ink);background:var(--paper);border:1px solid var(--line);padding:11px;min-height:44px}
button:focus-visible,select:focus-visible,input:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
header{background:var(--paper);border-bottom:1px solid var(--line)}.top,.wrap{max-width:1150px;padding:0 24px;margin:auto}
.top{min-height:78px;display:flex;align-items:center;justify-content:space-between;gap:15px;flex-wrap:wrap}
.brand{font-weight:800;letter-spacing:.16em;text-decoration:none}.brand em{font-style:normal;color:var(--accent)}.brand small{font:700 10px ui-monospace,monospace;letter-spacing:.18em;display:block;color:var(--muted)}
nav{display:flex;gap:18px;align-items:center}nav a{text-decoration:none;font-weight:700;font-size:13px}
.kicker{font:700 12px/1.5 ui-monospace,monospace;letter-spacing:.13em;text-transform:uppercase;color:var(--accent)}
.hero{padding:65px 0 45px;display:grid;grid-template-columns:1.5fr .5fr;gap:40px}
h1{font-size:clamp(42px,6vw,74px);line-height:1.04;letter-spacing:-.06em;margin:10px 0 24px}
h2{font-size:clamp(28px,4vw,44px);line-height:1.1;letter-spacing:-.05em;margin:10px 0 25px}
.hero p,.muted{color:var(--muted)}.aside{border-top:3px solid var(--accent);padding:16px}
.stats{display:flex;flex-wrap:wrap;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.stats>div{padding:20px 30px 20px 0;min-width:170px}.stats b{font-size:30px;display:block;line-height:1.1}.stats small{font-size:11px;color:var(--muted);text-transform:uppercase}
.controls{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:20px 0}
.controls label{display:grid;gap:7px;font:700 11px ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
article{display:grid;grid-template-columns:180px 1fr;gap:22px;border-bottom:1px solid var(--line);padding:23px 0}
article h3{margin:0 0 8px;font-size:22px;letter-spacing:-.03em;line-height:1.2}article h3 a{text-decoration:none}
aside small{color:var(--muted)}.tag{font:700 10px/1.5 ui-monospace,monospace;color:var(--accent);letter-spacing:.08em}
.line{margin:16px 0 4px;border-left:2px solid var(--line);padding-left:17px}
.line p{font-size:13px;margin:7px 0;color:var(--muted)}.line b{color:var(--ink)}
.notice{margin:46px 0;padding-top:20px;border-top:2px solid var(--accent)}.notice p{color:var(--muted);max-width:76ch}
footer{border-top:1px solid var(--line);padding:26px 0;margin-top:55px;font-size:13px;color:var(--muted)}
@media(max-width:730px){.hero,.controls,article{grid-template-columns:1fr}.stats>div{min-width:135px}.top{padding-top:15px;padding-bottom:15px}}
"""
def render(history:dict,relations:dict)->str:
    if history.get("schema")!="scout-source-history-v0" or relations.get("schema")!="scout-relations-v0":
        raise ValueError("Unsupported Scout data")
    if any(d.get("publication_authorized") is not False or d.get("outreach_authorized") is not False for d in (history,relations)):
        raise ValueError("Private-only sources required")
    node_by_url={n["url"]:n for n in relations["nodes"] if n["kind"]=="source"}
    if not all(s["url"] in node_by_url or s["current_sample_state"]=="NOT_IN_LATEST_SAMPLE" for s in history["sources"]):
        raise ValueError("Unreconciled history/source graph")
    e=lambda x:escape(str(x),quote=True)
    embedded=json.dumps({"records":history["sources"],"snapshots":history["snapshots"]},ensure_ascii=True).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    return """<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | Signal History</title><style>"""+CSS+"""</style></head><body>
<header><div class="top"><a class="brand" href="https://youtube.shareplane.malott.ai/">GHOST<em>MESH</em><small>READERS / SCOUT</small></a><nav><a href="#history">Signal history</a><a href="#method">Method</a><button id="theme">LIGHT / DARK</button></nav></div></header>
<main class="wrap"><section class="hero"><div><p class="kicker">GhostMesh / Scout · Observation history</p><h1>See what changed.<br>Know what didn't.</h1><p>A chronology of sampled public signals and their metadata links. A missing result means a sampling change, not a disappeared project.</p></div><div class="aside"><p class="kicker">History depth</p><h2>"""+str(len(history["snapshots"]))+""" snapshots</h2><p>Historical observations only. No social virality measured, no publication or outreach authorized.</p></div></section>
<div class="stats"><div><b>"""+str(history["counts"]["distinct_sources"])+"""</b><small>Distinct sources</small></div><div><b>"""+str(history["counts"]["seen_in_multiple_snapshots"])+"""</b><small>Repeat sightings</small></div><div><b>"""+str(history["counts"]["not_in_latest_sample"])+"""</b><small>Outside latest sample</small></div></div>
<section id="history"><p class="kicker">Observed / Not inferred</p><h2>Source timeline</h2>
<div class="controls"><label>Sample status<select id="state"><option value="all">All observations</option><option value="PRESENT">Present in latest</option><option value="NOT_IN_LATEST_SAMPLE">Absent from latest sample</option></select></label>
<label>Repeat history<select id="repeat"><option value="all">All frequencies</option><option value="repeated">Seen more than once</option><option value="single">Seen once</option></select></label>
<label>Find source<input id="query" type="search" placeholder="Title, URL, topic"></label></div>
<p id="count" role="status" aria-live="polite"></p><div id="results"></div><p id="empty" class="muted" hidden>No matching source observations.</p></section>
<section class="notice" id="method"><p class="kicker">Evidence limits</p><h2>A timeline is not a claim register.</h2>
<p>First seen and last seen mean first and last collection here. A topic delta indicates changing words in sampled metadata, not a scientific development. The sources were not continuously monitored. No authorship, collaboration, or genuine momentum is inferred from these observations.</p></section></main>
<footer><div class="wrap">GHOSTMESH / SCOUT · Private research · Context endures. Possibility evolves.</div></footer>
<script type="application/json" id="observations">"""+embedded+"""</script>
<script>
const data=JSON.parse(document.querySelector('#observations').textContent);
const select=document.querySelector('#state'),repeat=document.querySelector('#repeat'),query=document.querySelector('#query'),results=document.querySelector('#results');
const el=(tag,cl,text)=>{let e=document.createElement(tag);if(cl)e.className=cl;if(text!==undefined)e.textContent=text;return e;};
function draw(){results.replaceChildren();let count=0;const q=query.value.trim().toLowerCase();
for(const s of data.records){
 if(select.value!=='all'&&s.current_sample_state!==select.value)continue;
 if(repeat.value==='repeated'&&s.observation_count<2)continue;
 if(repeat.value==='single'&&s.observation_count!==1)continue;
 const topicText=s.observations.flatMap(x=>x.topics||[]).join(' ');
 if(q&&!(s.title+' '+s.url+' '+topicText).toLowerCase().includes(q))continue;
 const card=el('article'),rail=el('aside'),body=el('div');
 rail.append(el('span','tag',s.current_sample_state.replaceAll('_',' ')));
 rail.append(el('p','muted',s.observation_count+' sample'+(s.observation_count===1?'':'s')));
 body.append(el('h3'));
 const anchor=el('a','',s.title+' ↗');anchor.href=s.url;anchor.target='_blank';anchor.rel='noopener noreferrer';body.lastChild.append(anchor);
 const track=el('div','line');
 for(const obs of s.observations){const line=el('p');line.append(el('b','',obs.captured_utc+' · '));line.append(document.createTextNode((obs.topics||[]).length?obs.topics.join(', '):'No tracked topics'));track.append(line);}
 for(const change of s.changes){const line=el('p');line.append(el('b','',change.type.replaceAll('_',' ')+' · '));line.append(document.createTextNode(change.certainty));track.append(line);}
 body.append(track);card.append(rail,body);results.append(card);count++;
}
document.querySelector('#count').textContent=count+' sources shown';document.querySelector('#empty').hidden=count!==0;}
[select,repeat,query].forEach(x=>x.addEventListener('input',draw));draw();
document.querySelector('#theme').addEventListener('click',()=>{const x=document.documentElement;x.dataset.theme=x.dataset.theme==='light'?'dark':'light';});
</script></body></html>"""

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--history",required=True,type=Path)
    p.add_argument("--relations",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    get=lambda path:json.loads(path.read_text(encoding="utf-8"))
    a.out.write_text(render(get(a.history),get(a.relations)),encoding="utf-8")
    print(a.out)
if __name__=="__main__": main()
