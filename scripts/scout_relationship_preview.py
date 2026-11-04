"""Render an offline, interactive Scout relationship explorer from typed graph receipts."""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path

CSS = """
:root{color-scheme:dark;--bg:#101215;--paper:#17191d;--ink:#f1f2f3;--muted:#afb4bd;--accent:#ef4456;--rule:#40454d;--soft:#21252b}
html[data-theme=light]{color-scheme:light;--bg:#fbfaf8;--paper:#fff;--ink:#18191b;--muted:#5c6068;--accent:#be1939;--rule:#d2d2d2;--soft:#f0efed}
*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,-apple-system,sans-serif;color:var(--ink);background:var(--bg)}
button,input,select{font:inherit}a{color:inherit;text-underline-offset:3px}a:hover{color:var(--accent)}
button:focus-visible,a:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
header{background:var(--paper);border-bottom:1px solid var(--rule)}
.top{width:min(1190px,calc(100% - 40px));margin:auto;min-height:78px;display:flex;align-items:center;justify-content:space-between;gap:20px}
.brand{text-decoration:none;font-weight:800;letter-spacing:.13em}.brand em{font-style:normal;color:var(--accent)}.brand small{display:block;color:var(--muted);font:700 10px ui-monospace,monospace;letter-spacing:.21em}
.nav{display:flex;gap:20px;align-items:center}.nav a{font-size:13px;text-decoration:none;font-weight:700}
.theme{border:1px solid var(--rule);color:var(--ink);background:transparent;padding:8px 11px;cursor:pointer;font-size:12px;font-weight:750}
.wrap{width:min(1190px,calc(100% - 40px));margin:auto}
.hero{padding:70px 0 55px;display:grid;grid-template-columns:minmax(0,1.6fr) minmax(240px,.5fr);gap:50px}
.kicker{font:750 11px/1.5 ui-monospace,monospace;letter-spacing:.15em;text-transform:uppercase;color:var(--accent)}
h1{font-size:clamp(44px,6.5vw,80px);line-height:1.03;letter-spacing:-.065em;max-width:13ch;margin:13px 0 23px}
.lede{max-width:65ch;color:var(--muted);font-size:18px}
.summary{border-top:3px solid var(--accent);padding-top:18px}.summary strong{display:block;font-size:40px;letter-spacing:-.07em}.summary p{font-size:13px;color:var(--muted)}
.stats{border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);display:flex;gap:0}
.stats>div{padding:22px 30px 22px 0;min-width:180px}.stats>div+div{padding-left:30px;border-left:1px solid var(--rule)}
.stats b{display:block;font-size:32px;line-height:1}.stats small{font:700 11px/1.6 ui-monospace,monospace;color:var(--muted);text-transform:uppercase}
.section{margin-top:58px}h2{font-size:clamp(30px,3.8vw,47px);line-height:1.1;letter-spacing:-.05em;margin:12px 0 27px}
.controls{display:grid;grid-template-columns:minmax(190px,1fr) minmax(190px,1fr);gap:17px;padding:20px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.controls label{display:grid;gap:8px;color:var(--muted);font:700 11px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.09em}
.controls select,.controls input{border:1px solid var(--rule);background:var(--paper);color:var(--ink);padding:12px;min-height:46px;max-width:100%;font:15px system-ui}
.network{display:grid;grid-template-columns:minmax(250px,.7fr) minmax(0,1.4fr);gap:35px;margin:30px 0 70px}
.rail{border-top:2px solid var(--accent);padding:18px 0}.rail p{color:var(--muted);font-size:14px}
.rail .rule{border-top:1px solid var(--rule);margin:22px 0}
.source{border-top:1px solid var(--rule);padding:20px 0;display:grid;grid-template-columns:100px minmax(0,1fr);gap:20px}
.source h3{font-size:21px;line-height:1.2;letter-spacing:-.035em;margin:0 0 8px}.source h3 a{text-decoration:none}
.source p{color:var(--muted);font-size:13px;margin:7px 0}.source .type{font:700 10px ui-monospace,monospace;color:var(--accent);text-transform:uppercase}
.pill{font:700 10px ui-monospace,monospace;padding:5px 7px;border:1px solid var(--rule);display:inline-block;margin:3px 5px 3px 0;overflow-wrap:anywhere}
.empty{color:var(--muted);padding:30px 0}
footer{background:var(--paper);border-top:1px solid var(--rule);padding:32px 0;margin-top:50px;font-size:13px;color:var(--muted)}
@media(max-width:780px){.hero,.network,.controls{grid-template-columns:1fr}.stats{flex-wrap:wrap}.stats>div{min-width:140px}.source{grid-template-columns:1fr;gap:4px}.nav{gap:10px}}
"""

def render(graph: dict) -> str:
    if graph.get("schema") != "scout-relations-v0":
        raise ValueError("Unknown graph schema")
    if graph.get("publication_authorized") is not False or graph.get("outreach_authorized") is not False:
        raise ValueError("Graph grants disallowed authority")
    nodes=graph["nodes"];edges=graph["edges"]
    known={n["id"] for n in nodes}
    if len(known)!=len(nodes) or any(x["from"] not in known or x["to"] not in known for x in edges):
        raise ValueError("Broken or duplicate graph nodes")
    if any(x["relation"] not in ("METADATA_TOPIC_MATCH","OBSERVED_SOURCE_HANDLE") for x in edges):
        raise ValueError("Unexpected relationship type")
    sources=[n for n in nodes if n["kind"]=="source"]
    topics=sorted((n for n in nodes if n["kind"]=="topic"),key=lambda x:x["label"])
    handles=sorted((n for n in nodes if n["kind"]=="observed_handle"),key=lambda x:x["label"])
    safe_data=json.dumps({"nodes":nodes,"edges":edges},ensure_ascii=True).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    options=['<option value="all">All observed topics</option>']
    for item in topics:
        options.append(f'<option value="{escape(item["id"],quote=True)}">{escape(item["label"].replace("-"," ").title())}</option>')
    # All names/URLs are injected via textContent by client JS, not interpreted as HTML.
    return """<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | Relationship Intelligence</title><style>"""+CSS+"""</style></head><body>
<header><div class="top"><a href="https://youtube.shareplane.malott.ai/" class="brand">GHOST<em>MESH</em><small>READERS / SCOUT</small></a>
<div class="nav"><a href="#explorer">Explore</a><a href="#limits">Method</a><button type="button" id="theme" class="theme">LIGHT / DARK</button></div></div></header>
<main class="wrap"><section class="hero"><div><p class="kicker">GhostMesh / Scout · Owner-private exploration</p>
<h1>Follow the ideas.<br>Question the links.</h1>
<p class="lede">Trace sources through the subjects and public account handles they actually mention. A relationship here is a research lead, not a discovered collaborator.</p></div>
<aside class="summary"><p class="kicker">Observed signal graph</p><strong>"""+str(len(sources))+"""</strong><p>Public source nodes. No people independently identified, no same-story assertions, no outreach authorized.</p></aside></section>
<div class="stats"><div><b>"""+str(len(topics))+"""</b><small>Matched topics</small></div><div><b>"""+str(len(handles))+"""</b><small>Observed handles</small></div><div><b>"""+str(len(edges))+"""</b><small>Typed source links</small></div></div>
<section class="section" id="explorer"><p class="kicker">Relationship lens / Source ↔ Context</p><h2>Explore connected signals.</h2>
<div class="controls"><label>Research topic<select id="topic">"""+ "".join(options)+"""</select></label>
<label>Search titles or accounts<input id="query" type="search" placeholder="Search evidence nodes"></label></div>
<div class="network"><aside class="rail"><p class="kicker">Selected context</p><h3 id="context-title">All observed signals</h3>
<p id="context-body">Choose a topic to inspect connected sources. Observed account handles are not verified personal identities.</p>
<div class="rule"></div><p class="kicker">Evidence distinctions</p>
<p><strong>Metadata topic match</strong>: a title or description matched a topic vocabulary. It does not establish common claims.</p>
<p><strong>Observed source handle</strong>: a feed or repository path references an account. It does not establish an individual's identity.</p>
<p><strong>Sample state</strong>: seen again versus new to the sampled feed; this is not trend velocity.</p></aside>
<div><p id="count" aria-live="polite"></p><div id="results"></div><p class="empty" id="empty" hidden>No matching sources in this observed collection.</p></div></div></section>
<section class="section" id="limits"><p class="kicker">Review method</p><h2>No invented connections.</h2>
<p>Shared words can point to an opportunity for comparison. They do not prove two authors know each other, discuss the same event, or endorse the same conclusion. Sources remain unreviewed leads until content inspection and editorial challenge.</p>
<p>The view is an offline file generated from the VPS research sample; it is not a live network monitor or a public site page.</p></section></main>
<footer><div class="wrap">GHOSTMESH / SCOUT · Context endures. Possibility evolves. · Research only.</div></footer>
<script id="graph-data" type="application/json">"""+safe_data+"""</script>
<script>
const data=JSON.parse(document.querySelector('#graph-data').textContent);
const nodeMap=new Map(data.nodes.map(n=>[n.id,n]));
const sourceNodes=data.nodes.filter(n=>n.kind==='source');
const topic=document.querySelector('#topic'), query=document.querySelector('#query');
const results=document.querySelector('#results'), count=document.querySelector('#count');
const associated=new Map();
for(const edge of data.edges){if(!associated.has(edge.from))associated.set(edge.from,[]);associated.get(edge.from).push(edge);}
function element(tag, className, txt){const el=document.createElement(tag);if(className)el.className=className;if(txt!==undefined)el.textContent=txt;return el;}
function update(){
 const topicID=topic.value,q=query.value.trim().toLowerCase();results.replaceChildren();
 let visible=0;const context=nodeMap.get(topicID);
 document.querySelector('#context-title').textContent=context?.label?.replaceAll('-',' ')||'All observed signals';
 document.querySelector('#context-body').textContent=context?'All connected sources below share metadata vocabulary for this topic, not necessarily a single event or scientific claim.':'Use topic filters and search to inspect source–topic–account relationships.';
 for(const s of sourceNodes){
  const links=associated.get(s.id)||[];
  if(topicID!=='all'&&!links.some(e=>e.to===topicID))continue;
  const linked=links.map(e=>nodeMap.get(e.to)?.label||'');
  if(q&&!(s.title+' '+s.url+' '+linked.join(' ')).toLowerCase().includes(q))continue;
  const card=element('article','source');
  const rail=element('aside');rail.append(element('span','type',s.sample_state.replaceAll('_',' ')));rail.append(element('p','', 'Unreviewed source'));
  const detail=element('div'), heading=element('h3'), a=element('a','',s.title+' ↗');
  a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';heading.append(a);detail.append(heading);
  for(const edge of links){const label=nodeMap.get(edge.to);if(!label)continue;detail.append(element('span','pill',edge.relation==='METADATA_TOPIC_MATCH'?'TOPIC · '+label.label:'OBSERVED ACCOUNT · '+label.label));}
  detail.append(element('p','',s.url));card.append(rail,detail);results.append(card);visible++;
 }
 count.textContent=visible+' source'+(visible===1?'':'s')+' shown';
 document.querySelector('#empty').hidden=visible!==0;
}
topic.addEventListener('change',update);query.addEventListener('input',update);update();
document.querySelector('#theme').addEventListener('click',()=>{const root=document.documentElement;root.dataset.theme=root.dataset.theme==='light'?'dark':'light';});
</script></body></html>"""

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--graph",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    if args.out.exists():raise SystemExit("Refusing overwrite")
    data=json.loads(args.graph.read_text(encoding="utf-8"))
    args.out.write_text(render(data),encoding="utf-8")
    print(args.out)
if __name__=="__main__":main()
