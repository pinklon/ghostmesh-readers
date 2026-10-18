#!/usr/bin/env python3
"""Offline static-site contract checks (Python standard library only)."""
from pathlib import Path
from html.parser import HTMLParser
import sys
import re
import hashlib
import json
import xml.etree.ElementTree as ET

site = Path(__file__).resolve().parents[1] / "site"
host = "https://youtube.shareplane.malott.ai"
required = ("index.html","404.html","favicon.svg","robots.txt","sitemap.xml","site.webmanifest",
            "_headers","the-score-is-not-the-system/index.html",
            "when-software-becomes-legible/index.html",
            "the-agent-a-company-owns/index.html",
            "when-agents-become-the-customer/index.html",
            "the-funnel-is-not-the-frontier/index.html",
            "the-microscope-is-not-a-soul/index.html",
            "the-inbox-was-a-boundary/index.html",
            "autonomy-needs-an-interface/index.html",
            "make-good-work-inspectable/index.html",
            "make-good-work-inspectable/receipt.json",
            "a-challenge-is-not-a-verdict/index.html",
            "a-challenge-is-not-a-verdict/receipt.json",
            "the-key-was-the-boundary/index.html",
            "the-key-was-the-boundary/receipt.json",
            "the-scan-never-reached-the-login/index.html",
            "the-scan-never-reached-the-login/receipt.json",
            "ask-for-the-outcome-keep-the-boundary/index.html",
            "ask-for-the-outcome-keep-the-boundary/receipt.json")
errors = []
# Fail publication if any private media, caption or transcript artifact leaks into site/.
for candidate in site.rglob("*"):
    if not candidate.is_file():
        continue
    name = candidate.name.lower()
    suffix = candidate.suffix.lower()
    if suffix in {".vtt", ".srt", ".sbv", ".ass", ".mp4", ".m4a", ".mp3", ".webm", ".wav"} or (
        name.startswith(("transcript", "captions", "subtitles")) and suffix in {".txt", ".md", ".json"}
    ):
        errors.append("private source artifact in public site: " + str(candidate.relative_to(site)))
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
                       ("2DmP5etgh4U","when-agents-become-the-customer"),
                       ("BjO_JC6ujXs","the-funnel-is-not-the-frontier"),
                       ("2oH1NACBgS4","the-microscope-is-not-a-soul"),
                       ("rb4CTZjHCNg","the-inbox-was-a-boundary"),
                       ("DdbCtAScTsk","autonomy-needs-an-interface"),
                       ("Z8lf5oWKfj0","make-good-work-inspectable"),
                       ("YaK6cnET2IE","the-key-was-the-boundary"),
                       ("8DKqcbEy-HM","the-scan-never-reached-the-login"),
                       ("NarezKh3w4o","ask-for-the-outcome-keep-the-boundary")):
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
if not allowlist or re.findall(r"'([^']+)'",allowlist[1]) != ["ZhM29Ds-mBg","PseF3LyXQ04","HQXi4snP36I","2DmP5etgh4U","BjO_JC6ujXs","2oH1NACBgS4","rb4CTZjHCNg","DdbCtAScTsk","Z8lf5oWKfj0","YaK6cnET2IE","8DKqcbEy-HM","NarezKh3w4o"]:
    errors.append("homepage player allowlist must contain exactly the twelve source IDs")
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
# Fifth Video Deconstruction: narrator attribution, exact source chapters, and evidence limits.
fifth=(site/"the-funnel-is-not-the-frontier/index.html").read_text(encoding="utf8")
for marker in ("The Funnel Is Not the Frontier", "Video Deconstruction", "DevLogic",
               "October 12, 2026", "6:14", "374", "napkin math", "not Karpathy speaking",
               "https://i.ytimg.com/vi/BjO_JC6ujXs/hqdefault.jpg",
               "youtube-nocookie.com/embed/BjO_JC6ujXs?autoplay=1&start=",
               'id="player"', 'id="play"', "document.createElement('iframe')",
               '<details class="convergence">', "Evidence ledger", "1,086", "369.12",
               "70d36196dde825edb359ba1516913ea0c75b4438be63566a099890196e7e71d3"):
    if marker not in fifth: errors.append("fifth deconstruction missing "+marker)
if re.search(r"<iframe\b",fifth,re.I): errors.append("fifth player must wait for interaction")
if [int(x) for x in re.findall(r'data-start="(\d+)"',fifth)] != [0,78,155,224,300]:
    errors.append("fifth five source chapters drift")
for sec,label in ((0,"The sharp funnel explained"),(78,"The shallow end: chatbots and casual use"),
                  (155,"Frontier labs and agent swarms"),(224,"Three filters: ambition, jaggedness, access"),
                  (300,"Why the AI debate goes nowhere")):
    if label not in fifth or f'watch?v=BjO_JC6ujXs&amp;t={sec}s' not in fifth:
        errors.append("fifth source chapter label/fallback missing "+label)
for slug in ("the-score-is-not-the-system","when-software-becomes-legible",
             "the-agent-a-company-owns","when-agents-become-the-customer"):
    if f'href="/{slug}/"' not in fifth: errors.append("fifth missing cross-link "+slug)
for content in (home,fourth):
    if "READER 004" in content or "video deconstruction" not in content.lower():
        errors.append("fourth Video Deconstruction label correction lost")
if "Reader 005" in fifth or "READER 005" in home: errors.append("fifth uses retired Reader number")
if "Read GhostMesh’s interpretation of the AI capability gap" not in home:
    errors.append("fifth homepage editorial CTA missing")
# Sixth Video Deconstruction: grounded creator chapters, opt-in source player, careful status.
sixth=(site/"the-microscope-is-not-a-soul/index.html").read_text(encoding="utf8")
for marker in ("The Microscope Is Not a Soul", "Count Grey Matter", "November 12",
               "2oH1NACBgS4", "youtube-nocookie.com/embed/2oH1NACBgS4",
               "2f90fe08e68b94e00dd5a3ac25b486e682231412bc41dd94838500c467590609",
               "source publication date unverified", "GhostMesh thesis",
               "separate governance questions", "22 percent", "model welfare",
               "must remain under explicit human permissions", "Suleyman",
               "What should be tested next", "not yet effective"):
    if marker.casefold() not in sixth.casefold():
        errors.append("sixth missing contract: "+marker)
if re.search(r"<iframe\b",sixth,re.I):
    errors.append("sixth player must wait for interaction")
sixth_starts=[int(x) for x in re.findall(r'data-start="(\d+)"',sixth)]
if sixth_starts != [0,93,238,327,515,834,1008]:
    errors.append("sixth source chapters drift")
for sec in sixth_starts:
    if f'watch?v=2oH1NACBgS4&amp;t={sec}s' not in sixth:
        errors.append("sixth missing YouTube chapter fallback "+str(sec))
for href in ("https://www.anthropic.com/news/2026-usage-policy-update",
             "https://www.anthropic.com/research/emotion-concepts-function",
             "https://www.anthropic.com/research/tracing-thoughts-language-model"):
    if href not in sixth: errors.append("sixth missing primary evidence "+href)
if "The Microscope Is Not a Soul" not in home or 'data-video-id="2oH1NACBgS4"' not in home:
    errors.append("sixth homepage source/CTA missing")

# Seventh Video Deconstruction: transcript-derived chapters, source boundaries,
# opt-in player, and original editorial interpretation.
seventh=(site/"the-inbox-was-a-boundary/index.html").read_text(encoding="utf8")
for marker in ("The Inbox Was a Boundary", "AI Copium", "rb4CTZjHCNg",
               "https://i.ytimg.com/vi/rb4CTZjHCNg/hqdefault.jpg",
               "youtube-nocookie.com/embed/rb4CTZjHCNg", "document.createElement('iframe')",
               "0c407beb78cb38dcc942ba40ed9f79274f4cb0bb833f22eb657d4427e10ee6f5",
               "5fe94c71a95b6f6b4b629991737d6774eb32d55c8ab0706e7031ec3bad61f302",
               "machine transcript", "source publication date unverified", "model identity remains uncertain",
               "GhostMesh has not run that experiment", "https://swarmcha.se/posts/chinese-agent-fleet-full-report"):
    if marker.casefold() not in seventh.casefold():
        errors.append("seventh missing contract: "+marker)
if re.search(r"<iframe\b",seventh,re.I): errors.append("seventh player must wait for interaction")
seventh_starts=[int(x) for x in re.findall(r'data-start="(\d+)"',seventh)]
if seventh_starts != [0,40,135,305,473,665]: errors.append("seventh transcript chapter starts drift")
for sec in seventh_starts:
    if f'watch?v=rb4CTZjHCNg&amp;t={sec}s' not in seventh:
        errors.append("seventh missing YouTube chapter fallback "+str(sec))
if "The Inbox Was a Boundary" not in home or 'data-video-id="rb4CTZjHCNg"' not in home:
    errors.append("seventh homepage source/CTA missing")

# Eighth Video Deconstruction: source chapters, accountable autonomy, and opt-in playback.
eighth=(site/"autonomy-needs-an-interface/index.html").read_text(encoding="utf8")
for marker in ("Autonomy Needs an Interface", "Knuckle Up with Nakul", "Guillermo Rauch",
               "DdbCtAScTsk", "youtube-nocookie.com/embed/DdbCtAScTsk",
               "document.createElement('iframe')", "GhostMesh thesis", "Evidence ledger",
               "1320b9ad691d4403bc035a761780c8fc7b1c1fcc00e141a5441cbdcd3622c6f3",
               "GhostMesh has not run this experiment"):
    if marker.casefold() not in eighth.casefold():
        errors.append("eighth missing contract: "+marker)
if re.search(r"<iframe\b",eighth,re.I): errors.append("eighth player must wait for interaction")
eighth_starts=[int(x) for x in re.findall(r'data-start="(\d+)"',eighth)]
if eighth_starts != [121,448,873,1421,2147,2327,3099,3828]:
    errors.append("eighth creator chapter starts drift")
for sec in eighth_starts:
    if f'watch?v=DdbCtAScTsk&amp;t={sec}s' not in eighth:
        errors.append("eighth missing YouTube chapter fallback "+str(sec))
for source in ("https://vercel.com/blog/introducing-eve",
               "https://vercel.com/blog/vercel-for-enterprise-apps-and-agents"):
    if source not in eighth: errors.append("eighth missing primary documentation "+source)
if "Autonomy Needs an Interface" not in home or 'data-video-id="DdbCtAScTsk"' not in home:
    errors.append("eighth homepage source/CTA missing")

# Ninth Video Deconstruction: public claim receipt and private source custody.
ninth_dir=site/"make-good-work-inspectable"
ninth=(ninth_dir/"index.html").read_text(encoding="utf8")
for marker in ("Make Good Work Inspectable", "Z8lf5oWKfj0",
               "Take seriously / watch selectively", "The 45-minute interview is optional",
               "26:37", "32:03", "36:01", "spec-driven failure",
                "Private evidence custody",
                "download href=\"/make-good-work-inspectable/receipt.json\"",
               "document.createElement('iframe')", "Evidence ledger"):
    if marker.casefold() not in ninth.casefold():
        errors.append("ninth missing contract: "+marker)
if re.search(r"<iframe\b",ninth,re.I): errors.append("ninth player must wait for interaction")
if [int(x) for x in re.findall(r'data-start="(\d+)"',ninth)] != [264,975,1597,1923,2161]:
    errors.append("ninth selected chapter starts drift")
for sec in [264,975,1597,1923,2161]:
    if f'watch?v=Z8lf5oWKfj0&amp;t={sec}s' not in ninth:
        errors.append("ninth missing YouTube chapter fallback "+str(sec))
receipt_path=ninth_dir/"receipt.json"
if receipt_path.is_file():
    receipt=json.loads(receipt_path.read_text(encoding="utf8"))
    if receipt.get("source",{}).get("videoId")!="Z8lf5oWKfj0" or receipt.get("reasonPack",{}).get("verification")!="pass":
        errors.append("ninth receipt source or pack verification mismatch")
    if receipt.get("publicFiles"):
        errors.append("ninth receipt must not advertise private files as public")
    if "private" not in receipt.get("reasonPack",{}).get("publicationBoundary","").lower():
        errors.append("ninth receipt must declare private custody")
    if not receipt.get("editorial",{}).get("claimMap"):
        errors.append("ninth public claim map missing")
    if any(token in ninth for token in (
        '/make-good-work-inspectable/transcript.txt',
        '/make-good-work-inspectable/captions.vtt',
        '/make-good-work-inspectable/SHA256SUMS.txt'
    )):
        errors.append("ninth links to private source artifacts")
else:
    errors.append("ninth receipt missing")
if "Make Good Work Inspectable" not in home or 'data-video-id="Z8lf5oWKfj0"' not in home:
    errors.append("ninth homepage source/CTA missing")

# First Instagram Reader: explicit source, opt-in embed, opinionated editorial,
# sanitized public receipt and private source custody.
instagram_dir=site/"a-challenge-is-not-a-verdict"
instagram=(instagram_dir/"index.html").read_text(encoding="utf8")
for marker in ("A Challenge Is Not a Verdict", "DeUnZhWgPKd",
               "Watch the minute. Keep the habit. Test the objections.",
               "https://www.instagram.com/reel/DeUnZhWgPKd/",
               "https://www.instagram.com/reel/DeUnZhWgPKd/embed/",
               "document.createElement('iframe')", "00:48", "What the Reel says",
               'download href="/a-challenge-is-not-a-verdict/receipt.json"',
               "https://not-equal.org/content/pdf/misc/Perkins1991.pdf",
               "https://arxiv.org/abs/2403.01791"):
    if marker not in instagram: errors.append("Instagram Reader missing " + marker)
if re.search(r"<iframe\b",instagram,re.I): errors.append("Instagram player must wait for interaction")
if 'data-reel-id="DeUnZhWgPKd"' not in home or 'href="/a-challenge-is-not-a-verdict/"' not in home:
    errors.append("Instagram homepage source/editorial link missing")
instagram_receipt=json.loads((instagram_dir/"receipt.json").read_text(encoding="utf8"))
if instagram_receipt.get("source",{}).get("shortcode")!="DeUnZhWgPKd" or instagram_receipt.get("reasonPack",{}).get("verification")!="pass":
    errors.append("Instagram receipt source or ReasonPack verification mismatch")
if len(instagram_receipt.get("editorial",{}).get("claimMap",[]))!=4:
    errors.append("Instagram receipt claim map incomplete")
if instagram_receipt.get("reasonPack",{}).get("manifestSha256")!="ac0d0bf670fbc0d6b5937e96742b2268e5b80d537f49e0ccf662e299d5aee649":
    errors.append("Instagram receipt pack identity mismatch")
if "private" not in instagram_receipt.get("reasonPack",{}).get("publicationBoundary","").lower():
    errors.append("Instagram receipt must declare private custody")
if any(token in instagram for token in ("/a-challenge-is-not-a-verdict/transcript.txt","/a-challenge-is-not-a-verdict/transcript.srt")):
    errors.append("Instagram Reader links to private transcript")

# OpenCode Reader: incident scope, attribution limits, source links, and private pack receipt.
opencode_dir=site/"the-key-was-the-boundary"
opencode=(opencode_dir/"index.html").read_text(encoding="utf8")
for marker in ("The Key Was", "YaK6cnET2IE", "Watch the opening. Act on credentials.",
               "https://opencode.ai/v2/docs/console/providers/", "https://www.anthropic.com/research/distillation-defenses",
               "https://openai.com/index/disrupting-a-coordinated-model-distillation-campaign/",
               "youtube-nocookie.com/embed/YaK6cnET2IE", "document.createElement('iframe')",
               'download href="/the-key-was-the-boundary/receipt.json"'):
    if marker not in opencode: errors.append("OpenCode Reader missing " + marker)
if re.search(r"<iframe\b",opencode,re.I): errors.append("OpenCode player must wait for interaction")
opencode_receipt=json.loads((opencode_dir/"receipt.json").read_text(encoding="utf8"))
if opencode_receipt.get("source",{}).get("videoId")!="YaK6cnET2IE" or opencode_receipt.get("reasonPack",{}).get("verification")!="pass":
    errors.append("OpenCode receipt source or ReasonPack verification mismatch")
if len(opencode_receipt.get("editorial",{}).get("claimMap",[]))!=5:
    errors.append("OpenCode receipt claim map incomplete")
if opencode_receipt.get("reasonPack",{}).get("manifestSha256")!="b4da0f88f3adabe378bd50ece3c49cd24e57bdb530fc818fa8d71700e711bedb":
    errors.append("OpenCode receipt pack identity mismatch")
if "private" not in opencode_receipt.get("reasonPack",{}).get("publicationBoundary","").lower():
    errors.append("OpenCode receipt must declare private custody")

# Strix Reader: separate the manual target demonstration from the incomplete agent runs.
strix_dir=site/"the-scan-never-reached-the-login"
strix=(strix_dir/"index.html").read_text(encoding="utf8")
for marker in ("The Scan Never", "8DKqcbEy-HM", "Worth seven minutes if you evaluate security agents.",
               "https://docs.strix.ai/llm-providers/local", "https://docs.strix.ai/advanced/skills",
               "https://wstg.owasp.org/v4.2/2-Introduction/",
               "youtube-nocookie.com/embed/8DKqcbEy-HM", "document.createElement('iframe')",
               'download href="/the-scan-never-reached-the-login/receipt.json"'):
    if marker not in strix: errors.append("Strix Reader missing " + marker)
if re.search(r"<iframe\b",strix,re.I): errors.append("Strix player must wait for interaction")
strix_receipt=json.loads((strix_dir/"receipt.json").read_text(encoding="utf8"))
if strix_receipt.get("source",{}).get("videoId")!="8DKqcbEy-HM" or strix_receipt.get("reasonPack",{}).get("verification")!="pass":
    errors.append("Strix receipt source or ReasonPack verification mismatch")
if len(strix_receipt.get("editorial",{}).get("claimMap",[]))!=5:
    errors.append("Strix receipt claim map incomplete")
if strix_receipt.get("reasonPack",{}).get("manifestSha256")!="90f0f545e0ea7b8c7a847427e6c7a18d9f8d4290cbce176b263ed5453bf0748a":
    errors.append("Strix receipt pack identity mismatch")
if "private" not in strix_receipt.get("reasonPack",{}).get("publicationBoundary","").lower():
    errors.append("Strix receipt must declare private custody")

# Ambition Reader: primary-essay attribution, opt-in source playback, and pack identity.
ambition_dir = site / "ask-for-the-outcome-keep-the-boundary"
ambition = (ambition_dir / "index.html").read_text(encoding="utf8")
ambition_receipt = json.loads((ambition_dir / "receipt.json").read_text(encoding="utf8"))
for marker in ("NarezKh3w4o", "Felix Rieseberg", "RoboNuggets",
               "youtube-nocookie.com/embed/NarezKh3w4o",
               "felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/",
               'download href="/ask-for-the-outcome-keep-the-boundary/receipt.json"'):
    if marker not in ambition:
        errors.append("Ambition Reader missing " + marker)
if re.search(r"<iframe\b", ambition, re.I):
    errors.append("Ambition player must wait for interaction")
if ambition_receipt.get("source", {}).get("videoId") != "NarezKh3w4o" or ambition_receipt.get("reasonPack", {}).get("verification") != "pass":
    errors.append("Ambition receipt source or pack verification mismatch")
if ambition_receipt.get("reasonPack", {}).get("manifestSha256") != "a417606635fdb2a880c4793b51d20e02cc30d4349a8b080e62b4e8044d207f00":
    errors.append("Ambition receipt pack identity mismatch")
if len(ambition_receipt.get("editorial", {}).get("claimMap", [])) != 7:
    errors.append("Ambition receipt claim map incomplete")

# The canonical Reader brief applies to every new publication. Existing editions
# predating the requirement are grandfathered; all other Reader directories must
# carry a visible three-part brief and matching sanitized receipt fields.
legacy_reader_slugs = {
    "the-score-is-not-the-system", "when-software-becomes-legible",
    "the-agent-a-company-owns", "when-agents-become-the-customer",
    "the-funnel-is-not-the-frontier", "the-microscope-is-not-a-soul",
    "the-inbox-was-a-boundary", "autonomy-needs-an-interface",
    "make-good-work-inspectable", "a-challenge-is-not-a-verdict",
    "the-key-was-the-boundary",
}
for reader_path in site.glob("*/index.html"):
    slug = reader_path.parent.name
    if slug in legacy_reader_slugs:
        continue
    article = reader_path.read_text(encoding="utf8")
    receipt_file = reader_path.parent / "receipt.json"
    if not receipt_file.is_file():
        errors.append(f"Reader {slug} missing canonical receipt")
        continue
    receipt = json.loads(receipt_file.read_text(encoding="utf8"))
    for field, heading in (("overview", "What the video is about"),
                           ("whyItMatters", "Why you should care"),
                           ("ghostMeshTakeaway", "What GhostMesh takes away")):
        if not receipt.get("editorial", {}).get(field):
            errors.append(f"Reader {slug} receipt missing {field}")
        if heading not in article:
            errors.append(f"Reader {slug} missing brief heading: {heading}")
    brief_pos = article.find('id="at-a-glance"')
    source_pos = article.find('id="source"')
    if brief_pos < 0 or source_pos < 0 or brief_pos > source_pos:
        errors.append(f"Reader {slug} brief must precede source and detailed analysis")

# Share and footer controls are a contract on every published Reader.
for slug in ("the-score-is-not-the-system","when-software-becomes-legible",
             "the-agent-a-company-owns","when-agents-become-the-customer",
             "the-funnel-is-not-the-frontier","the-microscope-is-not-a-soul",
             "the-inbox-was-a-boundary","autonomy-needs-an-interface",
             "make-good-work-inspectable","a-challenge-is-not-a-verdict",
             "the-key-was-the-boundary","the-scan-never-reached-the-login",
             "ask-for-the-outcome-keep-the-boundary"):
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
for path in ("/","/the-score-is-not-the-system/","/when-software-becomes-legible/","/the-agent-a-company-owns/","/when-agents-become-the-customer/","/the-funnel-is-not-the-frontier/","/the-microscope-is-not-a-soul/","/the-inbox-was-a-boundary/","/autonomy-needs-an-interface/","/make-good-work-inspectable/","/a-challenge-is-not-a-verdict/","/the-key-was-the-boundary/","/the-scan-never-reached-the-login/","/ask-for-the-outcome-keep-the-boundary/"):
    if host+path not in urls: errors.append("sitemap missing "+path)
if errors:
    for x in errors: print("FAIL:",x)
    sys.exit(1)
print("PASS: required files, links, canonical hostname, sitemap, and source hygiene")
