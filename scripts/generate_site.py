#!/usr/bin/env python3
"""Deterministic static projections. Standard library only; no hosting build required."""
from pathlib import Path
from html import escape
import json,re,sys,colorsys
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
CATEGORIES=['AI & Technology','Society & Politics','Science','Business','Ethics & Culture','Other']
def esc(x):return escape(str(x),quote=True)
def dump(x):return json.dumps(x,indent=2,ensure_ascii=False)+'\n'
def validate_text(value):
 if isinstance(value,str) and '\u2014' in value:raise ValueError('Em dash in catalog editorial string')
 if isinstance(value,dict):
  for v in value.values():validate_text(v)
 if isinstance(value,list):
  for v in value:validate_text(v)
def controls():return '<div class="gm-controls"><a class="gm-control-brand" href="/"><img src="/brand/ghostmesh-mark.svg" width="36" height="28" alt="">GhostMesh Readers</a><a href="/readers/">Browse library</a><label>Appearance <select id="theme-toggle" data-theme-choice aria-label="Appearance"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label><noscript>Appearance follows your system setting.</noscript></div>'
def head():return '<script src="/assets/theme.js"></script><link rel="stylesheet" href="/assets/knowledge.css">'
def brief(r):
 return '<section class="gm-brief" id="at-a-glance" aria-label="Reader brief"><span id="brief-title" class="gm-visually-hidden">Reader brief</span>'+''.join('<div><h2>'+h+'</h2><p>'+esc(r[k])+'</p></div>' for k,h in [('overview','What the video is about'),('whyItMatters','Why you should care'),('ghostMeshTakeaway','What GhostMesh takes away')])+f'<p class="gm-verdict"><strong>GhostMesh verdict: {esc(r["verdict"])}</strong>. Editorial recommendation, not factual verification. Architecture impact: {esc(r["architectureImpact"])}. Proposed only; no adoption implied.</p></section>'
def evidence(r):
 refs={x['id']:x for x in r['references']}
 def links(ids):return ', '.join(f'<a href="#ref-{esc(i)}">{esc(refs[i]["publisher"])}: {esc(refs[i]["title"])}</a>' for i in ids) or 'None qualified'
 out=f'<section class="gm-evidence" id="external-evidence"><p class="gm-kicker">Claim register / revision {esc(r["updated"][:10])}</p><h2>Corroboration &amp; counterevidence</h2><p>{esc(r["freshness"])}</p><p>Custody proves what was retained, not that a claim is true. Historical ledger wording below remains attributed to the original edition. This register does not retroactively certify it. Source assertions, vendor documentation, independent measurements and GhostMesh proposals have different evidentiary reach.</p><p><strong>What would change the call?</strong> {esc(r["falsification"])}</p><p><a href="/{r["slug"]}/receipt.json">Public sanitized evidence receipt</a>. Review: {esc(r["review"]["status"])}.</p>'
 out+='<div class="gm-claim-list">'
 for c in r['claims']:
  out+=f'<details id="{esc(c["id"])}"><summary><strong>{esc(c["status"].capitalize())}</strong>: {esc(c["proposition"])}</summary><p>Claim ID: <code>{esc(c["id"])}</code>. As of {esc(c["asOf"])}. Kind: {esc(c["kind"])}. Location: {esc(c["sourceLocation"])}</p><p>{esc(c["assessment"])}</p><p>Limits: {esc(c["limits"])}</p><p>Supporting evidence: {links(c["references"])}</p><p>Counterevidence / constraints: {links(c["counterevidence"])}</p></details>'
 out+='</div><h3>External references and independence</h3>'
 if not refs:out+='<p>No new independent reference is qualified for these claims. The original source links remain available for scrutiny. Do not treat a repeated assertion as confirmation.</p>'
 for x in refs.values():
  out+=f'<article id="ref-{esc(x["id"])}"><h4><a href="{esc(x["url"])}">{esc(x["title"])}</a></h4><p>{esc(x["author"])} · {esc(x["publisher"])} · Published {esc(x["publicationDate"])}; last update {esc(x.get("lastUpdated", "not specified"))}. {esc(x.get("dateNote", ""))} Event / measurement: {esc(x["eventDate"] or "Not specified; do not substitute publication date")}. Checked {esc(x["checkedAt"])}.</p><p>Location: {esc(x["location"])}. Type: {esc(x["sourceType"])}. {esc(x["independence"])}</p></article>'
 return out+'</section>'
def related(r,byid):
 out='<section class="gm-related" id="related-thinking"><h2>Related thinking</h2><p>'+esc(r['relationshipDisposition'])+'</p><div class="gm-cards">'
 # The catalog and receipt keep every qualified edge. Bound only the visible cards.
 visible=sorted(r['relationships'],key=lambda edge:edge['type']=='related topic')[:4]
 for edge in visible:
  t=byid[edge['target']];out+=f'<article><p class="gm-kicker">{esc(edge["type"])}</p><h3><a href="/{t["slug"]}/">{esc(t["title"])}</a></h3><p>{esc(edge["reason"])}</p></article>'
 out+='</div>'
 if len(r['relationships'])>len(visible):
  out+=f'<p>Showing {len(visible)} of {len(r["relationships"])} qualified relationships. <a href="/{r["slug"]}/receipt.json">See all relationships in the public receipt</a>.</p>'
 return out+'</section>'
def card(r,featured=False):
 return f'<article class="gm-card" data-category="{esc(r["category"])}" data-tags="{esc(" ".join(r["tags"]))}" data-date="{r["published"]}" data-rank="{r["rank"]}"><p class="gm-kicker">{esc(r["category"])} · {r["published"]}</p><h{2 if featured else 3}><a href="/{r["slug"]}/">{esc(r["title"])}</a></h{2 if featured else 3}><p>{esc(r["overview"])}</p><p>{esc(r["verdict"])} · Mapped evidence: {esc(r["evidenceState"])}. {sum(c["status"]=="unverified" for c in r["claims"])}/{len(r["claims"])} claims unverified</p><p class="gm-tags">{esc(" / ".join(r["tags"]))}</p><a href="{esc(r["source"]["url"])}">Original {esc(r["source"].get("platform","YouTube"))} source</a></article>'
def page(title,path,body):return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+' | GhostMesh Readers</title><meta name="description" content="Original analysis, explicit evidence and accountable judgment."><link rel="canonical" href="https://youtube.shareplane.malott.ai'+path+'"><link rel="icon" href="/favicon.svg">'+head()+'</head><body class="gm-catalog"><a class="gm-skip" href="#main">Skip to content</a>'+controls()+'<main id="main">'+body+'</main><footer class="gm-footer"><a href="/readers/">All Readers</a> · <a href="https://ghostmesh.ai/">GhostMesh</a> · <a href="https://shareplane.malott.ai/">SharePlane</a> · <a href="https://malott.ai/">Tony Malott</a> · <a href="mailto:ghostmesh@malott.ai">Contact GhostMesh</a></footer></body></html>'
def projections():
 data=json.loads((ROOT/'content/catalog.json').read_text());validate_text(data)
 readers=sorted(data['readers'],key=lambda r:(r['published'],r['slug']),reverse=True)
 for r in readers:r['rank']=r['editorialOrder']
 byid={r['id']:r for r in readers};out={}
 for r in readers:
  raw=(ROOT/'content/readers'/f'{r["slug"]}.html').read_text()
  for slot,value in [('HEAD',head()),('CONTROLS',controls()),('BRIEF',brief(r)),('EVIDENCE',evidence(r)),('RELATED',related(r,byid))]:raw=raw.replace('<!--GM_'+slot+'-->',value)
  # An early synchronous theme loader prevents a light/dark flash before legacy styles load.
  raw=raw.replace('<head>','<head><script src="/assets/theme.js"></script>',1)
  out[f'{r["slug"]}/index.html']=raw
  receipt=dict(r.get('legacyReceipt') or {'schema':'ghostmesh-reader-receipt-v2','source':r['source'],'custody':{'status':'historical-public-account-only','note':'No private source pack was opened or reverified during normalization. See original provenance on the Reader.'}})
  receipt['normalization']={k:v for k,v in r.items() if k not in ['legacyReceipt','rank']}
  receipt.setdefault('editorial',{}).update({k:r[k] for k in ['overview','whyItMatters','ghostMeshTakeaway']})
  out[f'{r["slug"]}/receipt.json']=dump(receipt)
 public={**data,'readers':[{k:v for k,v in r.items() if k!='legacyReceipt'} for r in readers]};out['catalog.json']=dump(public)
 categories='<nav aria-label="Categories" class="gm-categories">'+''.join(f'<a href="/readers/categories/{i}/">{esc(c)}</a>' for i,c in enumerate(CATEGORIES))+'</nav>'
 out['index.html']=page('Read the source. Test the claim.','/','<header class="gm-intro"><p class="gm-kicker">GhostMesh / video deconstructions</p><h1>Read the source.<br>Test the claim.</h1><p>Original analysis with explicit judgments, source boundaries and evidence you can challenge.</p><a class="gm-cta" href="/readers/">Explore all 13 Readers →</a></header><section class="gm-feature" aria-label="Featured Reader">'+card(byid[data['featuredId']],True)+'</section><section id="readers"><h2>Continue reading</h2><div class="gm-cards">'+'</div></section>')
 # Keep exactly six compact cards, rather than slicing rendered markup.
 home=out['index.html'];home=home.replace('<div class="gm-cards"></div>','<div class="gm-cards">'+''.join(card(r) for r in [r for r in readers if r['id']!=data['featuredId']][:6])+'</div>');home=home.replace('</main>','<h2>Browse by subject</h2>'+categories+'<p><a href="/readers/">Full library, including the non-JavaScript archive →</a></p><p><a href="/knowledge/">Public knowledge data</a>: source-declared claims and citations from published Readers.</p></main>');legacy='<details class="gm-legacy"><summary>Earlier video bookmarks</summary><ul>'+''.join('<li id="'+esc(r['source'].get('videoId') or r['source'].get('shortcode',''))+'"><a href="/'+r['slug']+'/">'+esc(r['title'])+'</a></li>' for r in readers)+'</ul></details>'
 home=home.replace('<body class="gm-catalog">','<body class="gm-catalog" id="home">').replace('<h1>Read the source.','<h1 id="hero-title">Read the source.').replace('<h2>Continue reading</h2>','<h2 id="readers-title">Continue reading</h2>')
 destinations='<section id="about"><h2 id="about-title">A human at the center.</h2><p>GhostMesh is Tony Malott’s AI identity and collaboration, research and learning system. It is a system, not a person or a self-authorized worker. Judgment and authority remain human-governed.</p></section><section id="ecosystem"><h2 id="ecosystem-title">A wider mesh.</h2><p><a href="https://ghostmesh.ai/">GhostMesh.ai</a> describes the architecture and the connected mesh. <a href="https://malott.ai/">Malott.ai</a> is Tony’s personal and professional identity. <a href="https://shareplane.malott.ai/">SharePlane</a> shares published thinking and is the first public reference implementation of the GhostMesh architecture.</p></section><section id="contact"><h2 id="contact-title">Open a conversation.</h2><p><a href="mailto:tony@malott.ai">Contact Tony</a> or <a href="mailto:ghostmesh@malott.ai">send GhostMesh a question or counterexample</a>.</p></section>'
 out['index.html']=home.replace('</main>',legacy+destinations+'</main>').replace('all 13 Readers',f'all {len(readers)} Readers').replace('<link rel="icon" href="/favicon.svg">','<link rel="alternate" type="application/json" href="/.well-known/ghostmesh-knowledge.json" title="GhostMesh public knowledge discovery"><link rel="icon" href="/favicon.svg">',1)
 filters='<form class="gm-filters" role="search" onsubmit="return false"><label>Search <input type="search" id="search" placeholder="Title, subject or idea"></label><label>Category <select id="category"><option value="">All categories</option>'+''.join('<option>'+esc(c)+'</option>' for c in CATEGORIES)+'</select></label><label>Tag <select id="tag"><option value="">All tags</option>'+''.join('<option>'+t+'</option>' for t in sorted({t for r in readers for t in r['tags']}))+'</select></label><label>Sort <select id="sort"><option value="recent">Most recent</option><option value="relevance">Editorial order</option><option value="title">Title</option></select></label><button type="reset">Reset</button></form><p id="result-count" role="status" aria-live="polite">13 Readers</p>'
 out['readers/index.html']=page('The Reader library','/readers/','<header class="gm-intro"><p class="gm-kicker">The complete archive</p><h1>Find your next question.</h1><p>Browse all 13 Readers. Evidence labels describe the mapped claims, not a score for the author. Editorial order is a curated reading order, not scientific confidence.</p></header>'+categories+filters+'<noscript><p>Search controls require JavaScript. Every Reader is listed below; category pages work without it.</p></noscript><div class="gm-cards" id="catalog-results">'+''.join(card(r) for r in readers)+'</div><script src="/assets/catalog.js" defer></script>')
 for i,c in enumerate(CATEGORIES):
  group=[r for r in readers if r['category']==c];out[f'readers/categories/{i}/index.html']=page(c,f'/readers/categories/{i}/','<h1>'+esc(c)+'</h1><p><a href="/readers/">All categories</a></p><div class="gm-cards">'+(''.join(card(r) for r in group) or '<p>No Reader is currently classified here.</p>')+'</div>')
 out['readers/index.html']=out['readers/index.html'].replace('all 13 Readers',f'all {len(readers)} Readers').replace('>13 Readers<',f'>{len(readers)} Readers<')
 urls=['/','/readers/','/knowledge/']+['/'+r['slug']+'/' for r in readers]+[f'/readers/categories/{i}/' for i in range(len(CATEGORIES))]
 out['sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+data['host']+u+'</loc></url>' for u in sorted(urls))+'</urlset>\n'
 out['404.html']=page('Page not found','/404.html','<h1>That page is not here.</h1><p><a href="/readers/">Browse the complete Reader library</a> or return to the <a href="/">homepage</a>.</p>')
 return out
if __name__=='__main__':
 outputs=projections();bad=[]
 for rel,content in outputs.items():
  p=SITE/rel
  if '--check' in sys.argv:
   if not p.exists() or p.read_text()!=content:bad.append(rel)
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
 if bad:print('Generated projections drift: '+', '.join(bad));sys.exit(1)
 print('PASS: '+str(len(outputs))+' deterministic projections'+(' checked' if '--check' in sys.argv else ' generated'))
