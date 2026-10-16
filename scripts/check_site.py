#!/usr/bin/env python3
"""Offline static-site contract checks (Python standard library only)."""
from pathlib import Path
from html.parser import HTMLParser
import sys
import re
import xml.etree.ElementTree as ET

site = Path(__file__).resolve().parents[1] / "site"
host = "https://youtube.shareplane.malott.ai"
required = ("index.html","404.html","favicon.svg","robots.txt","sitemap.xml","site.webmanifest",
            "_headers","the-score-is-not-the-system/index.html",
            "when-software-becomes-legible/index.html",
            "the-agent-a-company-owns/index.html",
            "when-agents-become-the-customer/index.html")
errors = []
class Page(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"): self.ids.add(a["id"])
        if tag in ("a","link") and a.get("href"): self.links.append(a["href"])
for rel in required:
    p=site/rel
    if not p.is_file() or p.stat().st_size==0: errors.append("missing "+rel)
for p in site.rglob("*.html"):
    raw=p.read_text(encoding="utf8")
    parsed=Page(); parsed.feed(raw)
    if "https://readers.shareplane.malott.ai" in raw: errors.append("stale canonical "+str(p))
    if re.search(r"/Users/|/private/var/tmp/|/srv/ghostmesh/|ghp_[A-Za-z0-9]{20,}",raw):
        errors.append("private-source marker "+str(p))
    for href in parsed.links:
        if href.startswith("/") and not href.startswith("//"):
            path=(site/href.split("#",1)[0].split("?",1)[0].lstrip("/"))
            if not (path.is_file() or (path/"index.html").is_file()):
                errors.append(f"broken internal link {p.name}: {href}")
        elif href.startswith("#") and href[1:] and href[1:] not in parsed.ids:
            errors.append(f"broken anchor {p.name}: {href}")
    if p.name=="index.html" and f'<link rel="canonical" href="{host}' not in raw:
        errors.append("canonical mismatch "+str(p))
# Homepage contract: original thumbnails and opt-in in-page previews must remain
# prominent, while each article still has its own editorial action.
home=(site/"index.html").read_text(encoding="utf8")
for video_id,slug in (("ZhM29Ds-mBg","the-score-is-not-the-system"),
                       ("PseF3LyXQ04","when-software-becomes-legible"),
                       ("HQXi4snP36I","the-agent-a-company-owns"),
                       ("2DmP5etgh4U","when-agents-become-the-customer")):
    for marker in (f'i.ytimg.com/vi/{video_id}/hqdefault.jpg',
                   f'data-video-id="{video_id}"',
                   f'https://www.youtube.com/watch?v={video_id}',
                   f'href="/{slug}/"'):
        if marker not in home: errors.append("homepage video/editorial link missing "+marker)
if "youtube-nocookie.com/embed/" not in home or "reader-preview" not in home:
    errors.append("homepage click-to-play player missing")
for address in ("tony@malott.ai","ghostmesh@malott.ai"):
    if f"mailto:{address}" not in home: errors.append("homepage contact missing "+address)
for marker in ("first public reference implementation",
               "architecture and the connected mesh",
               "personal and professional identity"):
    if marker not in home: errors.append("homepage ecosystem description missing "+marker)
reader=(site/"the-score-is-not-the-system/index.html").read_text(encoding="utf8")
for marker in ("The Score Is Not the System","ZhM29Ds-mBg",'id="youtube-player"'):
    if marker not in reader: errors.append("Reader missing "+marker)
# The second Reader must retain the user's editorial/video-first acceptance criteria.
# These are static checks; real YouTube playback is checked separately in a browser.
second=(site/"when-software-becomes-legible/index.html").read_text(encoding="utf8")
for label in ("PseF3LyXQ04","youtube-nocookie.com/embed/PseF3LyXQ04",
              "www.youtube.com/watch?v=PseF3LyXQ04"):
    if label not in second: errors.append("Reader 002 missing source/playback "+label)
if "i.ytimg.com/vi/PseF3LyXQ04/" not in second:
    errors.append("Reader 002 must show real YouTube thumbnail")
chapters=[int(x) for x in re.findall(r'data-start="(\d+)"',second)]
expected=[0,65,189,218,268,343,529,661,800,990,1126,1192]
if chapters!=expected: errors.append("Reader 002 12 in-page chapter start points drift")
for name in ("Why REA is bigger than cloning software",
             "How Notion", "calculator", "Ledger Reborn", "What GhostMesh should consider"):
    if name.casefold() not in second.casefold():
        errors.append("Reader 002 missing chapter/implication "+name)
# Reader 003: source-only interview, opt-in player, and editorial boundaries.
third=(site/"the-agent-a-company-owns/index.html").read_text(encoding="utf8")
for marker in ("The Agent a Company Owns", "Riley Brown", "Guillermo Rauch",
               "https://i.ytimg.com/vi/HQXi4snP36I/hqdefault.jpg",
               "youtube-nocookie.com/embed/HQXi4snP36I", "54:22",
               "https://www.youtube.com/watch?v=HQXi4snP36I",
               'id="player"', 'id="play"', "document.createElement('iframe')",
               "What GhostMesh should consider", "Borrow /", "Experiment /", "Hold /",
               "9,655", "1,398", "3,253.477", "477,752", "399+140",
               "source-only", "default-OFF", "uncommissioned", "permissive",
               "October 15", "September 9", "August 6", "Tony Brain", "Library Atlas",
               "Hyperion", "Commons", "exactly-once", "Non-adoption", "Evidence ledger"):
    if marker not in third: errors.append("Reader 003 missing contract: "+marker)
if re.search(r"<iframe\b",third,re.I):
    errors.append("Reader 003 iframe must not exist before interaction")
starts=[int(x) for x in re.findall(r'data-start="(\d+)"',third)]
if starts != [0,81,446,618,872,1340,1631,2032,2430,2782,3185]:
    errors.append("Reader 003 11 chapter starts drift")
for sec in starts:
    if f'watch?v=HQXi4snP36I&amp;t={sec}s' not in third:
        errors.append(f"Reader 003 missing YouTube chapter fallback {sec}")
for slug in ("the-score-is-not-the-system", "when-software-becomes-legible"):
    if f'href="/{slug}/"' not in third:
        errors.append("Reader 003 missing earlier Reader "+slug)
for source in ("https://vercel.com/blog/introducing-eve", "https://github.com/vercel/eve",
               "https://github.com/vercel/eve/blob/main/packages/eve/README.md",
               "https://vercel.com/blog/agent-stack",
               "https://vercel.com/changelog/persistent-memory-for-eve-agents",
               "https://vercel.com/blog/vercel-ship-2026-recap",
               "https://vercel.com/kb/guide/github-agent-eve"):
    if f'href="{source}"' not in third: errors.append("Reader 003 missing source "+source)
allowlist=re.search(r"const allowed = new Set\(\[(.*?)\]\)",home)
if not allowlist or re.findall(r"'([^']+)'",allowlist[1]) != ["ZhM29Ds-mBg","PseF3LyXQ04","HQXi4snP36I","2DmP5etgh4U"]:
    errors.append("homepage player allowlist must contain exactly the four source IDs")
if "Explore GhostMesh's take on company agents" not in home:
    errors.append("homepage third editorial action missing")
# Reader 004: caption-grounded editorial, explicit comparisons, and opt-in seeks.
fourth=(site/"when-agents-become-the-customer/index.html").read_text(encoding="utf8")
for marker in ("When Agents Become the Customer", "How to build a $10B AI company (Supabase Co-Founder)",
               "David Ondrej", "Ant Wilson", "October 16, 2026", "50:26",
               "https://i.ytimg.com/vi/2DmP5etgh4U/hqdefault.jpg",
               "youtube-nocookie.com/embed/2DmP5etgh4U", 'id="player"', 'id="play"',
               "document.createElement('iframe')", "GHOSTMESH EDITORIAL CHAPTERS",
               '<details class="convergence">', "Independent Convergence / Disagreement",
               "snapshot as of Oct16, 2026", "Caption attribution", "Primary documentation",
               "GhostMesh inference", "9,452", "1,341", "2,649", "3,027.599",
               "What GhostMesh should consider", "Borrow /", "Experiment /", "Hold /",
               "not yet commissioned", "caption-grounded", "no substantiated position compared"):
    if marker not in fourth: errors.append("Reader 004 missing contract: "+marker)
if re.search(r"<iframe\b",fourth,re.I): errors.append("Reader 004 iframe must wait for interaction")
starts=[int(x) for x in re.findall(r'data-start="(\d+)"',fourth)]
if starts != [0,480,720,960,1200,1440,1680,2160,2640,2880]:
    errors.append("Reader 004 ten editorial chapter starts drift")
for sec in starts:
    if f'watch?v=2DmP5etgh4U&amp;t={sec}s' not in fourth:
        errors.append(f"Reader 004 missing chapter fallback {sec}")
if fourth.find('id="editorial-body"') > fourth.find('<details class="convergence">'):
    errors.append("Reader 004 thesis must precede comparison")
for slug in ("the-score-is-not-the-system","when-software-becomes-legible","the-agent-a-company-owns"):
    if f'href="/{slug}/"' not in fourth: errors.append("Reader 004 missing prior edition "+slug)
for source in ("https://supabase.com/blog/supabase-is-acquiring-turso",
               "https://supabase.com/blog/select-2026-build-anything",
               "https://supabase.com/blog/local-supabase-project-per-agent-with-or-without-docker",
               "https://supabase.com/blog/supabase-agent-skills",
               "https://supabase.com/docs/guides/auth/oauth-server/mcp-authentication",
               "https://supabase.com/blog/introducing-supabase-evals",
               "https://developers.openai.com/api/docs/guides/agents/sdk",
               "https://developers.openai.com/api/docs/guides/agents/guardrails-approvals",
               "https://platform.claude.com/docs/en/managed-agents/permission-policies",
               "https://github.com/QwenLM/Qwen-Agent",
               "https://api-docs.deepseek.com/guides/tool_calls/", "https://www.cloudroom.dev/about"):
    if f'href="{source}"' not in fourth: errors.append("Reader 004 missing primary source "+source)
if "Read GhostMesh’s take on agents as software customers" not in home:
    errors.append("homepage fourth editorial action missing")
# Share and footer controls are a contract on every published Reader.
for slug in ("the-score-is-not-the-system","when-software-becomes-legible",
             "the-agent-a-company-owns","when-agents-become-the-customer"):
    article=(site/slug/"index.html").read_text(encoding="utf8")
    for token in ('/brand/ghostmesh-mark.svg', '/assets/reader-chrome.css',
                  '/assets/reader-share.js', 'data-gm-share', 'data-copy-link',
                  'data-native-share', 'data-email-link', 'gm-reader-footer',
                  'href="/"','https://ghostmesh.ai/','https://shareplane.malott.ai/',
                  'https://malott.ai/','mailto:ghostmesh@malott.ai'):
        if token not in article:
            errors.append(f"Reader {slug} missing shared chrome: {token}")
    if '/.netlify/scripts/hud?' in article:
        errors.append(f"Reader {slug} includes captured Netlify-injected script")
for asset in ("assets/reader-chrome.css","assets/reader-share.js",
              "brand/ghostmesh-mark.svg"):
    if not (site/asset).is_file():
        errors.append("missing shared Reader asset: "+asset)
xml=ET.parse(site/"sitemap.xml")
urls=[x.text for x in xml.getroot().iter() if x.tag.endswith("loc")]
for path in ("/","/the-score-is-not-the-system/","/when-software-becomes-legible/","/the-agent-a-company-owns/","/when-agents-become-the-customer/"):
    if host+path not in urls: errors.append("sitemap missing "+path)
if errors:
    for x in errors: print("FAIL:",x)
    sys.exit(1)
print("PASS: required files, links, canonical hostname, sitemap, and source hygiene")
