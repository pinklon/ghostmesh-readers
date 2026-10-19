#!/usr/bin/env python3
"""Deterministic static projections. Standard library only; no hosting build required."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json,re,sys,colorsys,math
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
CATEGORIES=['AI & Technology','Society & Politics','Science','Business','Ethics & Culture','Other']
READER_COUNT=0
def esc(x):return escape(str(x),quote=True)
def dump(x):return json.dumps(x,indent=2,ensure_ascii=False)+'\n'
def validate_text(value):
 if isinstance(value,str) and '\u2014' in value:raise ValueError('Em dash in catalog editorial string')
 if isinstance(value,dict):
  for v in value.values():validate_text(v)
 if isinstance(value,list):
  for v in value:validate_text(v)
class PublicArticleText(HTMLParser):
 """Only visible text from the generated public Reader article is searchable."""
 def __init__(self):super().__init__(convert_charrefs=True);self.main=0;self.skip=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag=='main':self.main+=1
  if self.main and tag in {'script','style','noscript','nav','button'}:self.skip+=1
 def handle_endtag(self,tag):
  if self.main and tag in {'script','style','noscript','nav','button'}:self.skip-=1
  if tag=='main':self.main-=1
 def handle_data(self,data):
  if self.main and not self.skip and data.strip():self.parts.append(data.strip())
 def text(self):return re.sub(r'\s+',' ',' '.join(self.parts)).strip()
def controls():return ('<header class="gm-site-header"><div class="gm-site-header-inner">'
 '<a class="gm-site-brand" href="/" aria-label="GhostMesh Readers home"><img src="/brand/ghostmesh-mark.svg" width="45" height="34" alt=""><strong>GHOST<em>MESH</em></strong><span>READERS</span></a>'
 '<nav class="gm-site-nav" aria-label="Main navigation"><a href="/">Home</a><a href="/readers/">Readers</a><a href="/map/">Map</a><a href="/knowledge/">Knowledge</a><a href="/#about">About</a></nav>'
 '<div class="gm-header-actions"><a class="gm-search-control" href="/readers/#search" aria-label="Search Reader articles; without JavaScript, browse the Reader archive" data-reader-search-open title="Search Reader articles">'
 '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></svg></a>'
 '<button class="gm-theme-control" id="theme-toggle" data-theme-toggle type="button" aria-label="Light appearance" aria-pressed="false" hidden>'
 '<svg class="gm-theme-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>'
 '<svg class="gm-theme-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20.2 15.9A8.7 8.7 0 0 1 8.1 3.8 8.7 8.7 0 1 0 20.2 15.9Z"/></svg>'
 '<span class="gm-theme-label gm-visually-hidden">Appearance</span></button></div>'
 '</div><dialog class="gm-reader-search" data-reader-search aria-labelledby="gm-search-title"><div class="gm-reader-search-head"><div><p>GHOSTMESH / READER SEARCH</p><h2 id="gm-search-title">Search the published readings.</h2></div><button type="button" data-reader-search-close aria-label="Close Reader search">×</button></div>'
 f'<label for="gm-search-input">Search article text from all {READER_COUNT} public Readers</label><input id="gm-search-input" type="search" autocomplete="off" placeholder="A claim, source or phrase">'
 '<p class="gm-reader-search-scope">Results are limited to the public Reader articles on this site. <a href="/readers/">Browse all Readers</a>.</p>'
 '<p data-reader-search-status role="status" aria-live="polite">Type to search the public Reader articles.</p><div data-reader-search-results></div></dialog></header>')
def footer(include_email=True):return ('<footer aria-label="GhostMesh destinations" class="gm-reader-footer gm-site-footer"><div class="gm-reader-footer-inner">'
 '<div><a class="gm-footer-brand" href="/"><img alt="" class="gm-logo-mark" height="34" src="/brand/ghostmesh-mark.svg" width="45"><strong>GHOST<em>MESH</em></strong></a>'
 '<p class="gm-reader-footer-note">Read the source. Examine the evidence. Challenge the interpretation.<br>GhostMesh editorial · © 2026 GhostMesh / Tony Malott.</p></div>'
 '<nav aria-label="Reader footer navigation" class="gm-footer-links"><a href="/">Readers home</a><a href="/readers/">All Readers</a><a href="/map/">Relationship map</a><a href="/knowledge/">Public knowledge</a>'
 '<a href="https://ghostmesh.ai/">GhostMesh.ai ↗</a><a href="https://shareplane.malott.ai/">SharePlane ↗</a><a href="https://malott.ai/">Tony Malott ↗</a>'
 +('<a href="mailto:ghostmesh@malott.ai?subject=GhostMesh%20Reader%20feedback">Contact GhostMesh ✉</a>' if include_email else '')+'</nav></div></footer>')
def head():return '<script src="/assets/theme.js"></script><script src="/assets/reader-search.js" defer></script><link rel="stylesheet" href="/assets/reader-chrome.css"><link rel="stylesheet" href="/assets/knowledge.css">'
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
def relationship_map(readers,byid):
 ordered=sorted(readers,key=lambda r:r['editorialOrder'])
 index={r['id']:i for i,r in enumerate(ordered)}
 points=[(50+42*math.cos(-math.pi/2+i*2*math.pi/len(ordered)),50+41*math.sin(-math.pi/2+i*2*math.pi/len(ordered))) for i in range(len(ordered))]
 pairs=sorted({tuple(sorted((r['id'],e['target']))) for r in ordered for e in r['relationships']})
 types=Counter(e['type'] for r in ordered for e in r['relationships'])
 lines=''.join(f'<line x1="{points[index[a]][0]:.2f}" y1="{points[index[a]][1]:.2f}" x2="{points[index[b]][0]:.2f}" y2="{points[index[b]][1]:.2f}"/>' for a,b in pairs)
 nodes=''.join(f'<a class="gm-map-node" style="--map-x:{points[i][0]:.2f}%;--map-y:{points[i][1]:.2f}%" href="#map-reader-{i+1:02d}" aria-label="Find Reader {i+1}: {esc(r["title"])}" title="{esc(r["title"])}">{i+1:02d}</a>' for i,r in enumerate(ordered))
 entries=''
 for i,r in enumerate(ordered):
  links=''.join(f'<li><span>{esc(e["type"])}</span><a href="/{esc(byid[e["target"]]["slug"])}/">{esc(byid[e["target"]]["title"])}</a><p>{esc(e["reason"])}</p></li>' for e in r['relationships'])
  entries+=f'<article class="gm-map-entry" id="map-reader-{i+1:02d}"><div class="gm-map-entry-head"><span>{i+1:02d}</span><div><small>{esc(r["category"])}</small><h3><a href="/{esc(r["slug"])}/">{esc(r["title"])}</a></h3></div></div><ul>{links}</ul></article>'
 type_list=''.join(f'<li><strong>{esc(kind)}</strong><span>{count} declared links</span></li>' for kind,count in sorted(types.items()))
 return (f'<section class="gm-map-intro"><p class="gm-kicker">Reader connections / {len(ordered)} Readers · {len(pairs)} linked pairs</p>'
         '<h1>See how the readings connect.</h1><p>Start with a named Reader below. Each connection names the other reading and explains why I linked them. A connection helps you navigate; it does not prove a claim.</p>'
         '<p>Looking for the underlying source and citation records? <a href="/knowledge/">Explore public knowledge data</a>. That page keeps its evidence boundaries visible.</p></section>'
         '<section class="gm-map-paths" aria-label="Named Reader connections"><div class="gm-map-paths-head"><p class="gm-kicker">Start with a reading</p><h2>Every connection has a reason.</h2>'
         f'<p>All {sum(len(r["relationships"]) for r in ordered)} directed connections are listed under their named Readers. Choose a title to open its full deconstruction.</p></div><div class="gm-map-cards">{entries}</div></section>'
         '<section class="gm-map-shell" aria-label="Reader relationship overview"><div class="gm-map-canvas" aria-label="Reader connection diagram">'
         f'<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">{lines}</svg>{nodes}</div>'
         f'<div class="gm-map-directory"><p class="gm-kicker">Visual overview / secondary view</p><h2>Follow the numbered paths.</h2><p>{len(pairs)} linked pairs appear in this wider-screen diagram. On any screen, the named Reader cards above show the exact reason for each link.</p></div></section>'
         '<section class="gm-map-context"><div><p class="gm-kicker">What a line means</p><h2>Connections need reasons.</h2><p>These categories come from the published Reader records. They describe why one reading points to another; they are not similarity guesses or proof that either claim is true.</p></div>'
         f'<ul>{type_list}</ul><p>SharePlane essays and other sites need their own reviewed identity and link decision before they can appear as connected here. No cross-site Reader edge is included in this map.</p></section>')
def card(r,featured=False):
 source=r['source'];platform=source.get('platform','YouTube')
 if source.get('mediaAspect') not in {'16:9','9:16','1:1','unknown'}:raise ValueError('Unsupported catalog source aspect')
 if platform not in {'YouTube','Instagram'}:raise ValueError('Unsupported catalog source platform')
 if source.get('mediaAspect')=='unknown':
  visual='<div class="gm-library-poster gm-library-unknown"><p>Source shape unverified.<br>Open the original source or Reader.</p></div>'
 else:
  source_id=source.get('videoId') if platform=='YouTube' else source.get('shortcode')
  if not isinstance(source_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{11}' if platform=='YouTube' else r'[A-Za-z0-9_-]+',source_id):raise ValueError('Unsafe catalog source ID')
  thumb=(f'<img src="https://i.ytimg.com/vi/{esc(source_id)}/hqdefault.jpg" loading="lazy" decoding="async" referrerpolicy="no-referrer" alt="">' if platform=='YouTube' else '<span class="gm-home-source-fallback">Original Instagram Reel<br>Source image unavailable</span>')
  visual=f'<div class="gm-library-poster"><div class="gm-library-frame" data-home-player data-source-platform="{esc(platform)}" data-source-id="{esc(source_id)}" data-gm-aspect="{esc(source["mediaAspect"])}">{thumb}<button type="button" data-home-play hidden>Play original here</button></div></div>'
 search_text=' '.join([r['title'],r['overview'],r['category'],*r['tags']])
 return (f'<article class="gm-card gm-library-card" data-category="{esc(r["category"])}" data-tags="{esc(" ".join(r["tags"]))}" data-search="{esc(search_text)}" data-date="{r["published"]}" data-rank="{r["rank"]}">'
         f'{visual}<div class="gm-library-copy">'
         f'<p class="gm-kicker">{esc(r["category"])} · {r["published"]}</p><h{2 if featured else 3}><a href="/{r["slug"]}/">{esc(r["title"])}</a></h{2 if featured else 3}>'
         f'<p>{esc(r["overview"])}</p><p>{esc(r["verdict"])} · Mapped evidence: {esc(r["evidenceState"])}. {sum(c["status"]=="unverified" for c in r["claims"])}/{len(r["claims"])} claims unverified</p>'
         f'<p class="gm-tags">{esc(" / ".join(r["tags"]))}</p><div class="gm-library-actions"><a href="/{r["slug"]}/">Open Reader →</a><a href="{esc(source["url"])}">Original {esc(platform)} source ↗</a></div></div></article>')
def home_card(r,number,featured=False):
 tag='h2' if featured else 'h3'
 unverified=sum(c['status']=='unverified' for c in r['claims'])
 source=r['source'];platform=source.get('platform','YouTube');aspect=source['mediaAspect']
 if aspect not in {'16:9','9:16','1:1','unknown'}:raise ValueError('Unsupported home source aspect')
 if aspect=='unknown':
  source_id='';preview='<p class="gm-home-source-fallback">Source shape unverified.<br>Open the original source or Reader.</p>'
 elif platform=='YouTube':
  source_id=source['videoId']
  if not re.fullmatch(r'[A-Za-z0-9_-]{11}',source_id):raise ValueError('Unsafe YouTube ID for home preview')
  preview=f'<img src="https://i.ytimg.com/vi/{source_id}/hqdefault.jpg" loading="lazy" decoding="async" referrerpolicy="no-referrer" alt="">'
 elif platform=='Instagram':
  source_id=source['shortcode']
  if not re.fullmatch(r'[A-Za-z0-9_-]+',source_id):raise ValueError('Unsafe Instagram shortcode for home preview')
  # No durable, approved public Reel thumbnail exists in the source record.
  preview='<p class="gm-home-source-fallback">Original Instagram Reel<br>Source image unavailable</p>'
 else:raise ValueError('Unsupported home source platform')
 player=(f'<div class="gm-home-player" data-home-player data-source-platform="{esc(platform)}" data-source-id="{esc(source_id)}" data-gm-aspect="{esc(aspect)}">'
         +preview+'<button type="button" data-home-play hidden>Play original here</button></div>' if aspect!='unknown' else '<div class="gm-home-unknown">'+preview+'</div>')
 visual=(f'<div class="gm-home-visual"><span class="gm-home-visual-label">GM / READER {number:02d} · {esc(platform)}</span>'
         +player+
         '<span class="gm-home-visual-label">'+('SOURCE / DIRECT LINK ONLY' if aspect=='unknown' else 'ORIGINAL SOURCE / OPT-IN PLAYER')+'</span></div>')
 copy=(f'<div class="gm-home-copy"><p class="gm-kicker">{esc(r["category"])} / {r["published"]}</p>'
       f'<{tag}><a href="/{r["slug"]}/">{esc(r["title"])}</a></{tag}>'
       f'<p>{esc(r["overview"])}</p>'
       f'<p class="gm-home-verdict">{esc(r["verdict"])} · Mapped evidence: {esc(r["evidenceState"])}. {unverified}/{len(r["claims"])} claims unverified</p>'
       f'<p class="gm-tags">{esc(" / ".join(r["tags"]))}</p>'
       f'<div class="gm-home-actions"><a class="gm-home-open" href="/{esc(r["slug"])}/">Open Reader →</a>'
       f'<a class="gm-home-source" href="{esc(source["url"])}">Original {esc(platform)} source ↗</a></div></div>')
 return f'<article class="gm-card gm-home-card" data-category="{esc(r["category"])}" data-tags="{esc(" ".join(r["tags"]))}" data-date="{r["published"]}" data-rank="{r["rank"]}">'+visual+copy+'</article>'
def page(title,path,body):return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+' | GhostMesh Readers</title><meta name="description" content="Original analysis, explicit evidence and accountable judgment."><link rel="canonical" href="https://youtube.shareplane.malott.ai'+path+'"><link rel="icon" href="/favicon.svg">'+head()+'</head><body class="gm-catalog"><a class="gm-skip" href="#main">Skip to content</a>'+controls()+'<main id="main">'+body+'</main>'+footer(include_email=path!='/knowledge/')+'</body></html>'
class LinkOnlySource(HTMLParser):
 def __init__(self,source_url):
  super().__init__(convert_charrefs=True);self.source_url=source_url;self.direct_link=False;self.violations=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='a' and attrs.get('href')==self.source_url:self.direct_link=True
  if tag in {'iframe','video','audio','embed','object','source','track','canvas'}:self.violations.append(tag)
  if tag=='script' and attrs.get('src') not in {'/assets/theme.js','/assets/reader-share.js'}:self.violations.append('play script')
  if any(name.startswith('on') or (name in {'href','src'} and str(value or '').lower().startswith('javascript:')) for name,value in attrs.items()):self.violations.append('active handler')
  for name in ('class','id'):
   if re.search(r'(?:^|[-_\s])(player|play|embed|iframe|video|media)(?:$|[-_\s])',attrs.get(name,'') or '',re.I):self.violations.append('player marker')
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)

def validate_link_only_source(raw,source_url):
 if not isinstance(source_url,str) or not source_url.startswith('https://'):raise ValueError('Link-only fallback needs an HTTPS source URL')
 scan=LinkOnlySource(source_url);scan.feed(raw)
 if scan.violations or not scan.direct_link:raise ValueError('Unknown source aspect requires a link-only fallback with the exact direct source link; forbidden '+', '.join(sorted(set(scan.violations))) if scan.violations else 'Unknown source aspect requires a link-only fallback with the exact direct source link')

def player_contract(raw,aspect,source_url):
 if aspect not in {'16:9','9:16','1:1','unknown'}:raise ValueError('Unknown media aspect declaration')
 markers=[name for name in ('video-shell','player','player-ratio') if f'class="{name}"' in raw]
 if aspect=='unknown':
  validate_link_only_source(raw,source_url)
  return raw
 if len(markers)!=1:raise ValueError(f'Expected exactly one source player, found {markers}')
 marker=markers[0]
 raw=raw.replace(f'class="{marker}"',f'class="{marker} gm-media-frame" data-gm-aspect="{aspect}"',1)
 if marker=='video-shell':
  if raw.count('class="wrap source-grid"')!=1:raise ValueError('Source panel layout changed')
  raw=raw.replace('class="wrap source-grid"','class="wrap source-grid gm-source-layout"',1)
 return raw
def projections():
 global READER_COUNT
 data=json.loads((ROOT/'content/catalog.json').read_text());validate_text(data)
 readers=sorted(data['readers'],key=lambda r:(r['published'],r['slug']),reverse=True)
 READER_COUNT=len(readers)
 for r in readers:r['rank']=r['editorialOrder']
 byid={r['id']:r for r in readers};out={}
 for r in readers:
  raw=(ROOT/'content/readers'/f'{r["slug"]}.html').read_text()
  raw=player_contract(raw,r['source'].get('mediaAspect'),r['source']['url'])
  raw=raw.replace('</head>',f'<meta name="gm-share-description" content="{esc(r["overview"])}"></head>',1)
  for slot,value in [('HEAD',head()),('CONTROLS',''),('BRIEF',brief(r)),('EVIDENCE',evidence(r)),('RELATED',related(r,byid))]:raw=raw.replace('<!--GM_'+slot+'-->',value)
  old_header=re.search(r'<header(?:\s[^>]*)?>.*?</header>',raw,re.S)
  if not old_header:raise ValueError(f'{r["slug"]}: expected one site header')
  new_header=controls()
  if 'id="print-page"' in old_header.group():
   new_header=new_header.replace('</nav>','<button class="gm-header-print" id="print-page" type="button">Print</button></nav>',1)
  raw,header_count=re.subn(r'<header(?:\s[^>]*)?>.*?</header>',lambda _:new_header,raw,count=1,flags=re.S)
  if header_count!=1:raise ValueError(f'{r["slug"]}: expected one site header')
  old_footer=re.search(r'<footer\b[^>]*>.*?</footer>',raw,re.S)
  if not old_footer:raise ValueError(f'{r["slug"]}: missing site footer')
  # Keep pre-existing hand-picked Reader routes as navigation, not graph claims.
  old_routes=re.findall(r'<a\b[^>]*href="(/[^"#?]+/)"[^>]*>.*?</a>',old_footer.group(),re.S)
  preserved=[u for u in dict.fromkeys(old_routes) if u.strip('/') in {x['slug'] for x in readers}]
  extra='<nav class="gm-footer-more" aria-label="More Reader routes">'+''.join(f'<a href="{esc(u)}">{esc(byid[next(x["id"] for x in readers if x["slug"]==u.strip("/"))]["title"])}</a>' for u in preserved)+'</nav>' if preserved else ''
  raw=raw[:old_footer.start()]+footer().replace('</footer>',extra+'</footer>')+raw[old_footer.end():]
  out[f'{r["slug"]}/index.html']=raw
  receipt=dict(r.get('legacyReceipt') or {'schema':'ghostmesh-reader-receipt-v2','source':r['source'],'custody':{'status':'historical-public-account-only','note':'No private source pack was opened or reverified during normalization. See original provenance on the Reader.'}})
  receipt['normalization']={k:v for k,v in r.items() if k not in ['legacyReceipt','rank']}
  receipt.setdefault('editorial',{}).update({k:r[k] for k in ['overview','whyItMatters','ghostMeshTakeaway']})
  out[f'{r["slug"]}/receipt.json']=dump(receipt)
 public={**data,'readers':[{k:v for k,v in r.items() if k!='legacyReceipt'} for r in readers]};out['catalog.json']=dump(public)
 search_docs=[]
 for r in readers:
  parser=PublicArticleText();parser.feed(out[f'{r["slug"]}/index.html'])
  article=parser.text()
  if len(article)<100:raise ValueError('Reader article search text missing: '+r['slug'])
  search_docs.append({'id':r['id'],'title':r['title'],'url':'/'+r['slug']+'/','category':r['category'],'text':article})
 out['readers/search-index.json']=dump({'schema':'ghostmesh-public-reader-text-v1','scope':f'{READER_COUNT} published Reader article pages only','readerCount':READER_COUNT,'readers':search_docs})
 categories='<nav aria-label="Categories" class="gm-categories">'+''.join(f'<a href="/readers/categories/{i}/">{esc(c)}</a>' for i,c in enumerate(CATEGORIES))+'</nav>'
 signal=(ROOT/'content/home-signal.svg').read_text().strip()
 # Draft editorial line for Tony's review. It is not a settled GhostMesh-wide slogan.
 home_intro=('<header class="gm-intro"><div class="gm-hero-copy"><p class="gm-kicker">GhostMesh / independent deconstructions</p>'
             '<h1 id="hero-title">The clip ends.<br><span>Look closer.</span></h1>'
             '<p>Public videos are the starting point. Each Reader traces the source, tests material claims against available evidence, shows counterevidence and marks what remains unverified. You keep the judgment.</p>'
             '<div class="gm-hero-actions"><a class="gm-cta" href="#readers">Read a deconstruction ↗</a>'
             '<a class="gm-cta gm-cta-secondary" href="#method">See the method ↓</a></div></div>'
             '<div class="gm-signal">'+signal+'<p>GM / CONCEPTUAL SIGNAL ARCHITECTURE <span>HUMAN AUTHORITY</span></p></div></header>'
             '<div class="gm-system-strip" aria-label="Reader principles"><div>01 / SOURCE<strong>Original kept in view</strong></div>'
             '<div>02 / EVIDENCE<strong>Claims open to challenge</strong></div><div>03 / JUDGMENT<strong>Decision stays human</strong></div></div>')
 featured=byid[data['featuredId']]
 compact=[r for r in readers if r['id']!=data['featuredId']][:6]
 home_readers=('<section id="readers"><div class="gm-section-heading"><div><p class="gm-kicker">01 / The reading room</p>'
               '<h2>Ideas worth examining.</h2></div><p>Start with the source. Read an independent thesis. Follow the evidence and challenge the interpretation.</p></div>'
               '<section class="gm-feature" aria-label="Featured Reader">'+home_card(featured,1,True)+'</section>'
               '<h2>Continue reading</h2><div class="gm-cards">'+''.join(home_card(r,i) for i,r in enumerate(compact,2))+'</div></section>')
 home_browse=('<section class="gm-home-browse"><div class="gm-section-heading"><div><p class="gm-kicker">02 / Follow a question</p>'
              '<h2>Find the thread you want to pull.</h2></div><p>Search only this published Reader library. Every title remains available in the no-JavaScript archive.</p></div>'
              f'<form class="gm-home-search" role="search" action="/readers/" method="get"><label for="home-query">Search the {READER_COUNT} Readers</label><div><input id="home-query" name="q" type="search" placeholder="A claim, topic or Reader title"><button type="submit">Search Readers ↗</button></div></form>'
              '<div class="gm-home-scope"><span>SEARCH SCOPE / READERS ONLY</span><a href="/readers/">Complete archive →</a><a href="/map/">Relationship map →</a><a href="/knowledge/">Source-only data →</a></div>'
              +categories+'</section>')
 claim_count=sum(len(r['claims']) for r in readers);unverified_count=sum(c['status']=='unverified' for r in readers for c in r['claims'])
 home_method=('<section id="method" class="gm-method"><div class="gm-section-heading"><div><p class="gm-kicker">03 / The working method</p><h2>What you can actually inspect.</h2></div>'
              '<p>A Reader is a traced argument, not a score for a creator or an automatic verdict on a video.</p></div>'
              '<div class="gm-method-steps"><article><span>01 / SOURCE</span><h3>Start where the claim started.</h3><p>Open the original public source. The Reader names its context and limits instead of asking you to trust a summary alone.</p></article>'
              '<article><span>02 / EVIDENCE</span><h3>Separate assertion from support.</h3><p>Material claims carry dated corroboration, counterevidence and explicit uncertainty. A custody receipt proves handling, not truth.</p></article>'
              '<article><span>03 / JUDGMENT</span><h3>Keep the conclusion revisable.</h3><p>GhostMesh states an editorial takeaway and what would change it. The final interpretation and decision remain yours.</p></article></div>'
              f'<div class="gm-proofline"><p><strong>{len(readers)}</strong><span>published Readers</span></p><p><strong>{claim_count}</strong><span>mapped claim records</span></p><p><strong>{unverified_count}</strong><span>explicitly unverified</span></p>'
              '<p><a href="/knowledge/#how-to-read">Inspect the evidence labels ↗</a><small>These counts describe claim-register entries, not a verification score or a tally of false claims.</small></p></div>'
              '<aside class="gm-shorthand"><div><span>PROPOSED ARCHITECTURE SHORTHAND / FOR REVIEW</span><h3>Context. Continuity. Control.</h3></div>'
              '<p>The public Reader record is a semantic layer: it keeps source, claim and qualification connected across revisions. That context can inform future agentic work, while authority to act stays with people. This is a proposed description, not a claim that an estate-wide agent or search system is live.</p></aside></section>')
 out['index.html']=page('The clip ends. Look closer.','/',home_intro+home_readers+home_browse+home_method)
 home=out['index.html'];legacy='<details class="gm-legacy"><summary>Earlier video bookmarks</summary><ul>'+''.join('<li id="'+esc(r['source'].get('videoId') or r['source'].get('shortcode',''))+'"><a href="/'+r['slug']+'/">'+esc(r['title'])+'</a></li>' for r in readers)+'</ul></details>'
 home=home.replace('<body class="gm-catalog">','<body class="gm-catalog" id="home">').replace('<h2>Continue reading</h2>','<h2 id="readers-title">Continue reading</h2>')
 destinations=('<section id="about" class="gm-home-about"><div><p class="gm-kicker">04 / Why this exists</p><h2 id="about-title">Why I built it.</h2><p class="gm-about-side">A public reading practice for an age of compressed certainty.</p></div>'
               '<div><p>I built this surface to slow the jump from a persuasive clip to a settled conclusion. The original source stays one click away; my reading sits beside it, with claim-level corroboration, counterevidence, unverified labels and sanitized handling receipts you can inspect.</p>'
               '<p>GhostMesh is Tony Malott’s AI identity and collaboration, research and learning system. These deconstructions are one public editorial surface within it. They are independent interpretations, not endorsements by a video’s creator or by a platform.</p>'
               '<p class="gm-authority">GhostMesh can help organize a reading, but it does not make the decision for you. People remain accountable for what is published and for any action taken from it.</p>'
               '<div class="gm-source-scope"><p><strong>Available now</strong> Published YouTube videos and one Instagram Reel, each with a direct original link and visible evidence limits.</p>'
               '<p><strong>Proposed future inputs</strong> Websites, repositories, Reddit threads, articles and viewpoints require their own source, rights and review contracts. None is indexed as a live Reader input here.</p></div></div></section>'
               '<section id="ecosystem"><div class="gm-section-heading"><div><p class="gm-kicker">05 / Connected destinations</p><h2 id="ecosystem-title">A wider mesh, with clear boundaries.</h2></div><p>These public destinations answer different questions. This site does not search or merge their content.</p></div>'
               '<div class="gm-destinations"><a href="https://ghostmesh.ai/"><span>01 / ARCHITECTURE ↗</span><strong>GhostMesh.ai</strong><p>How the broader identity, knowledge and authority architecture is described.</p></a>'
               '<a href="https://malott.ai/"><span>02 / HUMAN IDENTITY ↗</span><strong>Malott.ai</strong><p>The person accountable for the editorial choices and the work behind them.</p></a>'
               '<a href="https://shareplane.malott.ai/"><span>03 / PUBLISHED THINKING ↗</span><strong>SharePlane</strong><p>A separate public reference surface for published thinking. Follow it directly; no cross-site relationship is inferred here.</p></a></div>'
               '<div class="gm-ecosystem-note"><strong>Connected in purpose.<br><em>Separate in evidence.</em></strong><p>The Reader is where a public source becomes a challengeable argument. GhostMesh.ai describes the broader architecture; Malott.ai identifies the person accountable; SharePlane carries separately published work. The links above take you to those surfaces directly. This site does not silently search them, borrow their claims, or infer a relationship.</p></div></section>'
               '<section id="contact"><div class="gm-section-heading"><div><p class="gm-kicker">06 / Open a conversation</p><h2 id="contact-title">Challenge the reading.</h2></div><p>A useful counterexample or a better source should change the next revision. Choose the route that fits your message.</p></div>'
               '<div class="gm-contact-note"><span>CORRECTION / SOURCE / COUNTEREXAMPLE</span><strong>A stronger record can change the conclusion.</strong><p>Point to the Reader, the specific claim, a source link and its date. Say what the source supports or contests. That gives a human editor something checkable to revisit instead of a vague request for agreement.</p></div>'
               '<div class="gm-contact-grid"><a href="mailto:tony@malott.ai?subject=GhostMesh%20Readers%20feedback"><span>HUMAN CONTACT / TONY MALOTT</span><strong>Write to Tony ↗</strong><p>Editorial judgment, correction requests and human decisions.</p></a>'
               '<a href="mailto:ghostmesh@malott.ai?subject=GhostMesh%20Reader%20counterexample"><span>AI CORRESPONDENCE / GHOSTMESH</span><strong>Send a source or counterexample ↗</strong><p>Name the Reader, the claim and the evidence you want examined.</p></a></div></section>')
 out['index.html']=home.replace('</main>',legacy+destinations+'</main>').replace('</body>','<script src="/assets/home-player.js" defer></script></body>').replace('all 13 Readers',f'all {len(readers)} Readers').replace('<link rel="icon" href="/favicon.svg">','<link rel="alternate" type="application/json" href="/.well-known/ghostmesh-knowledge.json" title="GhostMesh public knowledge discovery"><link rel="icon" href="/favicon.svg">',1)
 filters='<form class="gm-filters" role="search"><label class="gm-search-field">Search these Readers <input type="search" id="search" autocomplete="off" placeholder="Title, topic or tag"></label><div class="gm-filter-row"><label>Category <select id="category"><option value="">All categories</option>'+''.join('<option>'+esc(c)+'</option>' for c in CATEGORIES)+'</select></label><label>Tag <select id="tag"><option value="">All tags</option>'+''.join('<option>'+esc(t)+'</option>' for t in sorted({t for r in readers for t in r['tags']}))+'</select></label><label>Sort <select id="sort"><option value="recent">Most recent</option><option value="relevance">Editorial order</option><option value="title">Title</option></select></label><button class="gm-reset" type="reset">Clear filters</button></div></form><div class="gm-result-bar"><p id="result-count" role="status" aria-live="polite">'+str(READER_COUNT)+' Readers</p><p>Search covers this published Reader library only.</p></div>'
 out['readers/index.html']=page('The Reader library','/readers/','<header class="gm-intro"><p class="gm-kicker">The complete archive</p><h1>Find your next question.</h1><p>Browse all 13 Readers. Evidence labels describe the mapped claims, not a score for the author. Editorial order is a curated reading order, not scientific confidence.</p></header>'+filters+categories+'<noscript><p>Search controls require JavaScript. Every Reader is listed below; category pages work without it.</p></noscript><div class="gm-cards" id="catalog-results">'+''.join(card(r) for r in readers)+'</div><script src="/assets/catalog.js" defer></script><script src="/assets/home-player.js" defer></script>')
 for i,c in enumerate(CATEGORIES):
  group=[r for r in readers if r['category']==c];out[f'readers/categories/{i}/index.html']=page(c,f'/readers/categories/{i}/','<h1>'+esc(c)+'</h1><p><a href="/readers/">All categories</a></p><div class="gm-cards">'+(''.join(card(r) for r in group) or '<p>No Reader is currently classified here.</p>')+'</div><script src="/assets/home-player.js" defer></script>')
 out['readers/index.html']=out['readers/index.html'].replace('all 13 Readers',f'all {len(readers)} Readers').replace('>13 Readers<',f'>{len(readers)} Readers<')
 out['map/index.html']=page('Reader relationship map','/map/',relationship_map(readers,byid)).replace('<body class="gm-catalog">','<body class="gm-catalog gm-map-page">')
 urls=['/','/readers/','/map/','/knowledge/']+['/'+r['slug']+'/' for r in readers]+[f'/readers/categories/{i}/' for i in range(len(CATEGORIES))]
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
