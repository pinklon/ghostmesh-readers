#!/usr/bin/env python3
"""Offline publication gates: projections, evidence mapping, routes and public boundary."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from datetime import datetime,date,timezone
import json,os,re,sys,xml.etree.ElementTree as ET
from generate_site import projections,CATEGORIES,validate_text,validate_link_only_source,validate_paper_source,validate_article_source,validate_media_source
from editorial_depth import validate_reader as validate_editorial_depth
from scout_feed import validate_scout,validate_events
from scout_pages import validate_editions,review_url,edition_url
from scout_research import validate_research
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site'
VERDICTS={'Essential','Worth studying','Interesting, unproven','Mostly recycled','Misleading','Not worth your time'}
STATES={'corroborated','partially corroborated','contradicted','disputed','unverified'}
RELATIONS={'examines same claim','extends','challenges','responds to','shares entity','informs architecture','related topic'}
# This static site publishes only reviewed text assets. New asset formats require
# an explicit policy change, so an unfamiliar capture container fails closed.
PUBLIC_TEXT_EXTENSIONS={'.html','.json','.jsonld','.js','.css','.svg','.xml','.webmanifest'}
PUBLIC_TEXT_PATHS={'robots.txt','_headers','llms.txt'}
SOURCE_EXTENSIONS=set('.vtt .srt .sbv .ass .ssa .sub .ttml .dfxp .scc .sami .smi .lrc .srv1 .srv2 .srv3 .json3 .mkv .mka .mks .mp4 .m4a .m4v .mp3 .webm .wav .wave .mov .qt .ogg .ogv .oga .opus .flac .aac .aiff .aif .avi .wmv .wma .asf .flv .f4v .mpeg .mpg .mpe .m2v .ts .mts .m2ts .3gp .3g2 .vob .amr .ape .ac3 .aax'.split())
def capture_signature(data):
 return (data.startswith((b'\x1a\x45\xdf\xa3',b'OggS',b'fLaC',b'ID3',b'FLV',b'#!AMR',b'WEBVTT'))
         or data[:4] in (b'RIFF',b'FORM')
         or data[4:8] in (b'ftyp',b'moov',b'mdat')
         or data.startswith((b'\x00\x00\x01\xba',b'\x00\x00\x01\xb3')))
def source_custody_errors(reader):
 """Check honest public receipt labels; private evidence itself stays outside Git."""
 slug=reader['slug'];receipt=reader.get('legacyReceipt') or {};custody=receipt.get('custody') or {}
 errors=[]
 if not custody.get('status') or not custody.get('note'):
  errors.append(f'{slug}: source custody status and limits required')
 source=receipt.get('source') or {}
 if source.get('url')!=reader['source'].get('url') or source.get('videoId')!=reader['source'].get('videoId'):
  errors.append(f'{slug}: receipt source identity mismatch')
 pack=receipt.get('reasonPack') or {}
 if custody.get('status')=='qualified-private-pack-verified':
  if pack.get('verification')!='pass' or not re.fullmatch(r'[0-9a-f]{64}',pack.get('manifestSha256','')):
   errors.append(f'{slug}: verified pack claim lacks a manifest digest')
 else:
  if pack.get('verification')=='pass':errors.append(f'{slug}: unverified custody claims pack verification')
  inspection=receipt.get('sourceInspection') or {}
  if not all(inspection.get(k) for k in ('method','caveat','publicationBoundary')):
   errors.append(f'{slug}: limited source inspection needs method, caveat and privacy boundary')
  if not any(re.fullmatch(r'[0-9a-f]{64}',v) for k,v in inspection.items() if k.lower().endswith('sha256') and isinstance(v,str)):
   errors.append(f'{slug}: limited source inspection needs a retained-source digest')
 return errors
class Page(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.text=[];self.hide=0;self.tags=[];self.frames=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs);self.tags.append((t,a))
  if t in ('script','style'):self.hide+=1
  if a.get('id'):self.ids.append(a['id'])
  for k in ('href','src'):
   if a.get(k):self.links.append(a[k])
  if t=='iframe':self.frames.append(a)
  for k in ('content','alt','title','aria-label'):
   if a.get(k):self.text.append(a[k])
 def handle_endtag(self,t):
  if t in ('script','style'):self.hide-=1
 def handle_data(self,d):
  if not self.hide:self.text.append(d)
def check(root=ROOT):
 site=root/'site';errors=[]
 event_pr=None
 if os.environ.get('GITHUB_EVENT_NAME')=='pull_request':
  try:
   event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
   event_pr=event['number']
   if not isinstance(event_pr,int) or isinstance(event_pr,bool) or event_pr<1:raise ValueError
  except (OSError,KeyError,ValueError,TypeError):
   return ['GitHub pull request identity unavailable for editorial gate']
 require_merged=os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_REF')=='refs/heads/main'
 # Reject links before parsing any public file; never read through to a private target.
 links=[p for p in site.rglob('*') if p.is_symlink()]
 if links:return [f'Public symlink: {p.relative_to(site)}' for p in links]
 def require(ok,msg):
  if not ok:errors.append(msg)
 try:data=json.loads((root/'content/catalog.json').read_text());validate_text(data)
 except (ValueError,KeyError) as e:return ['Catalog: '+str(e)]
 try:
  scout=validate_scout(json.loads((root/'content/scout-public.json').read_text()))
  editions=validate_editions(json.loads((root/'content/scout-editions.json').read_text()),scout)['editions']
  validate_events(json.loads((root/'content/public-release-events.json').read_text()),data,scout)
  research=validate_research(json.loads((root/'content/scout-research.json').read_text()),scout,json.loads((root/'content/public-release-events.json').read_text()),root)
 except (ValueError,KeyError,TypeError,FileNotFoundError) as e:return ['Scout/feed source: '+str(e)]
 def timestamp(value, label):
  try:
   parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
   require(parsed.tzinfo is not None,label+': timezone required')
   if parsed.tzinfo:require(parsed<=datetime.now(timezone.utc),label+': future timestamp')
  except (ValueError,TypeError):errors.append(label+': invalid timestamp')
 readers=data['readers'];ids={r['id'] for r in readers};slugs={r['slug'] for r in readers}
 baseline=json.loads((root/'docs/baseline-audit.json').read_text())['readers']
 require({r['slug'] for r in baseline}<=slugs,'Existing permalink removed')
 require(len(ids)==len(readers)==len(slugs),'Duplicate Reader identity')
 require(data['schemaVersion']==1,'Unknown schema version')
 all_claims=[c['id'] for r in readers for c in r['claims']]
 require(len(all_claims)==len(set(all_claims)),'Duplicate global claim identity')
 pages={}
 for p in site.rglob('*.html'):
  raw=p.read_text();a=Page();a.feed(raw);pages[p]=a
  require(len(a.ids)==len(set(a.ids)),f'Duplicate HTML ID: {p.relative_to(site)}')
  require('—' not in ''.join(a.text),f'Em dash in rendered strings: {p.relative_to(site)}')
  if p.name=='index.html':require(any(t=='link' and x.get('rel')=='canonical' and x.get('href')==data['host']+'/'+str(p.parent.relative_to(site)).replace('.','').strip('/')+('/' if p.parent!=site else '') for t,x in a.tags),f'Canonical URL: {p.relative_to(site)}')
  for frame in a.frames:require(frame.get('src','') in ('','about:blank'),f'Player loads before opt-in: {p.relative_to(site)}')
 for p,a in pages.items():
  for href in a.links:
   u=urlsplit(href)
   if u.scheme or u.netloc:continue
   target=site/u.path.lstrip('/') if u.path.startswith('/') else p.parent/u.path
   if not u.path:target=p
   if target.is_dir():target=target/'index.html'
   require(target.is_file(),f'Broken local link {p.relative_to(site)}: {href}')
   if u.fragment and target in pages:require(unquote(u.fragment) in pages[target].ids,f'Broken fragment {p.relative_to(site)}: {href}')
 for old in baseline:
  p=site/old['slug']/'index.html';raw=p.read_text()
  require(set(old.get('anchorIds',[]))<=set(pages[p].ids),'Historical anchor removed: '+old['slug'])
  require(re.findall(r'data-start="(\d+)"',raw)==old.get('chapterStarts',[]),'Chapter timestamps drift: '+old['slug'])
 for r in readers:
  slug=r['slug'];p=site/slug/'index.html';raw=p.read_text();a=pages[p]
  errors.extend(validate_editorial_depth(root,r,event_pr=event_pr,require_merged=require_merged))
  timestamp(r['updated'],slug+' updated')
  try:date.fromisoformat(r['published'])
  except ValueError:errors.append(slug+': invalid publication date')
  require(r['published']<=r['updated'][:10],slug+': publication after revision')
  require(r['evidenceState']!='partially corroborated' or any(c['status'] in {'corroborated','partially corroborated'} for c in r['claims']),f'{slug}: aggregate evidence promotion')
  require(r['category'] in CATEGORIES and r['verdict'] in VERDICTS,f'Unknown classification {slug}')
  require(r['architectureImpact'] in {'none','watch','investigate','experiment recommended','change proposed'},f'Architecture impact {slug}')
  require(all(r.get(k) for k in ['overview','whyItMatters','ghostMeshTakeaway','published','updated','source','variant','claims','review']),f'Incomplete Reader {slug}')
  if r['source'].get('kind')=='paper':
   try:validate_paper_source(raw,r['source'])
   except ValueError as exc:errors.append(f'{slug}: {exc}')
   require('mediaAspect' not in r['source'] and 'platform' not in r['source'],f'{slug}: paper has video-only fields')
   require('gm-media-frame' not in raw and 'data-gm-aspect' not in raw,f'{slug}: paper has a fabricated media frame')
  elif r['source'].get('kind')=='article':
   try:validate_article_source(raw,r['source'])
   except ValueError as exc:errors.append(f'{slug}: {exc}')
   require('mediaAspect' not in r['source'] and 'platform' not in r['source'],f'{slug}: article has video-only fields')
   require('gm-media-frame' not in raw and 'data-gm-aspect' not in raw,f'{slug}: article has a fabricated media frame')
  else:
   try:validate_media_source(r['source'])
   except ValueError as exc:errors.append(f'{slug}: {exc}')
   if slug not in {old['slug'] for old in baseline}:errors.extend(source_custody_errors(r))
   aspect=r['source'].get('mediaAspect')
   require(aspect in {'16:9','9:16','1:1','unknown'},f'{slug}: source aspect missing or invalid')
   if aspect!='unknown':
    require(raw.count('gm-media-frame')==1 and raw.count(f'data-gm-aspect="{aspect}"')==1,f'{slug}: shared source player or aspect missing')
    require('gm-source-layout' in raw or 'class="player gm-media-frame"' in raw or 'class="player-ratio gm-media-frame"' in raw,f'{slug}: source player layout missing')
   else:
    try:validate_link_only_source(raw,r['source']['url'])
    except ValueError as exc:errors.append(f'{slug}: {exc}')
  for marker in ['at-a-glance','external-evidence','related-thinking']:require(marker in a.ids,f'{slug}: missing {marker}')
  require('data-theme-toggle' in raw and '/assets/theme.js' in raw,f'{slug}: theme missing')
  require(raw.find('id="at-a-glance"')<min([pos for token in ['data-gm-aspect=','id="source"','class="theater"'] if (pos:=raw.find(token))>=0] or [len(raw)]),f'{slug}: brief after source')
  receipt=json.loads((site/slug/'receipt.json').read_text());require(receipt['normalization']['id']==r['id'],f'{slug}: receipt identity')
  refs={x['id']:x for x in r['references']};require(len(refs)==len(r['references']),f'{slug}: duplicate reference IDs')
  require(len({c['id'] for c in r['claims']})==len(r['claims']),f'{slug}: duplicate claim IDs')
  for ref in refs.values():
   require(all(ref.get(k) for k in ['title','author','publisher','url','publicationDate','location','sourceType','independence','evidenceFamily','checkedAt']),f'{slug}: incomplete reference {ref["id"]}')
   require(urlsplit(ref['url']).scheme=='https',f'{slug}: unsafe reference URL')
   timestamp(ref['checkedAt'],slug+' evidence checked')
   value=ref['publicationDate'];precision=ref.get('datePrecision')
   if value=='unknown':require(bool(ref.get('dateNote')),slug+': unknown date needs explanation')
   else:
    pattern={'year':r'\d{4}','month':r'\d{4}-\d{2}','day':r'\d{4}-\d{2}-\d{2}'}.get(precision,'^$')
    require(bool(re.fullmatch(pattern,value)),slug+': date precision mismatch')
    try:date.fromisoformat(value+('-01-01' if precision=='year' else '-01' if precision=='month' else ''))
    except ValueError:errors.append(slug+': invalid source date')
    require(value<=ref['checkedAt'][:len(value)],slug+': source date after check')
  for c in r['claims']:
   require(c['status'] in STATES and all(c.get(k) for k in ['id','proposition','kind','asOf','assessment','limits','sourceLocation']),f'{slug}: incomplete claim {c.get("id")}')
   require(set(c['references']+c['counterevidence'])<=set(refs),f'{slug}: dangling reference')
   require(c['status']=='unverified' or c['references'] or c['counterevidence'],f'{slug}: confirmation from empty evidence')
   try:date.fromisoformat(c['asOf'])
   except ValueError:errors.append(f'{slug}: invalid asOf')
   if c.get('independentSourceCount'):
    families={refs[i]['evidenceFamily'] for i in c['references']};require(c['independentSourceCount']<=len(families),f'{slug}: duplicate independence')
  for edge in r['relationships']:
   require(edge['target'] in ids and edge['target']!=r['id'] and edge['type'] in RELATIONS and bool(edge['reason']) and bool(edge['provenance']),f'{slug}: unqualified relation')
   for link in edge['provenance']:
    u=urlsplit(link);q=site/u.path.strip('/')/'index.html';require(q in pages and (not u.fragment or u.fragment in pages[q].ids),f'{slug}: broken relation provenance {link}')
  require(bool(r.get('relationshipDisposition','').strip()),f'{slug}: missing relation disposition')
  assessment=r.get('relationshipReview') or {}
  try:
   reviewed_value=assessment.get('reviewedAt','')
   if not isinstance(reviewed_value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',reviewed_value):
    raise ValueError('relationship review date must use YYYY-MM-DD')
   reviewed=date.fromisoformat(reviewed_value)
   require(reviewed<=datetime.now(timezone.utc).date(),f'{slug}: future relationship review')
  except (ValueError,TypeError):errors.append(f'{slug}: missing or invalid relationship review date')
  require(assessment.get('reviewedCatalogSize')==len(readers),f'{slug}: stale relationship review catalog size')
  targets=[edge['target'] for edge in r['relationships']]
  require(len(targets)==len(set(targets)),f'{slug}: duplicate relationship target')
  require(assessment.get('reviewedTargets')==targets,f'{slug}: relationship review targets differ from catalog edges')
  require(assessment.get('decision')==('linked' if targets else 'none'),f'{slug}: relationship review decision does not match edges')
  require(len(str(assessment.get('rationale','')).strip())>=80,f'{slug}: relationship review needs a substantive rationale, including justified none')
 # Scan all public files, including unlinked assets and JSON, rather than only HTML.
 for p in root.rglob('*'):
  if '.git' in p.parts or '__pycache__' in p.parts:continue
  if p.is_relative_to(site) and p.is_symlink():
   errors.append(f'Public symlink: {p.relative_to(site)}');continue
  if not p.is_file():continue
  require(p.suffix.lower() not in SOURCE_EXTENSIONS,f'Private source media: {p.relative_to(root)}')
  require(not p.name.lower().startswith(('transcript','captions','subtitles')),f'Private source artifact: {p.relative_to(root)}')
  if p.is_relative_to(site):
   require(p.suffix.lower() in PUBLIC_TEXT_EXTENSIONS or p.relative_to(site).as_posix() in PUBLIC_TEXT_PATHS,f'Unapproved public file type: {p.relative_to(site)}')
   payload=p.read_bytes()
   require(not capture_signature(payload),f'Private source capture signature: {p.relative_to(site)}')
   try:payload.decode('utf-8')
   except UnicodeDecodeError:
    errors.append(f'Non-text public asset: {p.relative_to(site)}');continue
   require(b'\x00' not in payload,f'Binary public asset: {p.relative_to(site)}')
  if p.is_relative_to(site) and p.suffix in {'.html','.json','.jsonld','.js','.css','.xml'}:
   raw=p.read_text();require(not re.search(r'/Users/|/srv/ghostmesh/|/private/var/|gh[pousr]_[A-Za-z0-9]{20,}|(?:X-Amz-Signature|access_token|client_secret)=',raw),f'Private marker: {p.relative_to(site)}')
   if p.suffix in {'.json','.jsonld'}:
    try:validate_text(json.loads(raw))
    except ValueError:errors.append(f'Em dash JSON: {p.relative_to(site)}')
 home=(site/'index.html').read_text();require(len(re.findall(r'class="[^"]*\bgm-card\b[^"]*"',home))==7,'Homepage must have one feature and six cards')
 library=(site/'readers/index.html').read_text();require(len(re.findall(r'class="[^\"]*\bgm-card\b[^\"]*"',library))==len(readers),'Non-JS archive incomplete')
 sitemap=ET.parse(site/'sitemap.xml');urls=[x.text for x in sitemap.getroot().iter() if x.tag.endswith('loc')]
 try:ET.parse(site/'feed.xml')
 except ET.ParseError:errors.append('Invalid RSS XML')
 expected={data['host']+u for u in ['/','/readers/','/map/','/knowledge/','/scout/','/scout/archive/','/scout/research/','/scout/method/','/scout/essays/']}|{data['host']+record['url'] for record in research['records']}|{data['host']+edition_url(edition) for edition in editions}|{data['host']+'/'+s+'/' for s in slugs}|{data['host']+f'/readers/categories/{i}/' for i in range(6)}
 require(set(urls)==expected and len(urls)==len(expected),'Sitemap drift')
 if root==ROOT:
  for rel,content in projections().items():require((site/rel).read_text()==content,'Generated drift: '+rel)
 return errors
if __name__=='__main__':
 errors=check()
 for e in errors:print('FAIL:',e)
 if errors:sys.exit(1)
 print('PASS: all Readers, projections, evidence mapping, relationships, URLs, sitemap, editorial text and public boundary')
