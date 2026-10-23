"""Scout Signal Intake v0: public, read-only, bounded multi-source discovery.

Signals are leads, not endorsements. No credentials, crawling, posting, or outreach.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

MAX_BYTES=450_000
UA="GhostMesh-Scout/0.1 (+research-only; no contact or posting)"
FEEDS={
 "independent-builder":("https://simonwillison.net/atom/everything/","builder"),
 "huggingface":("https://huggingface.co/blog/feed.xml","research"),
 "cloudflare":("https://blog.cloudflare.com/rss/","engineering"),
 "lobsters":("https://lobste.rs/rss","community"),
 "github-engineering":("https://github.blog/feed/","engineering"),
 "arxiv-ai":("https://export.arxiv.org/rss/cs.AI","research")
}
GITHUB_QUERIES=("agent memory","agent authorization")
HN_URL="https://hacker-news.firebaseio.com/v0/topstories.json"
API_GITHUB="https://api.github.com/search/repositories"
def fetch(url: str) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/rss+xml, application/atom+xml, application/json, application/xml"})
    with urllib.request.urlopen(req,timeout=8) as response:
        if response.status!=200: raise ValueError("Unexpected HTTP status")
        payload=response.read(MAX_BYTES+1)
        if len(payload)>MAX_BYTES: raise ValueError("Oversized feed response")
        return payload

def clean(s):
    return re.sub(r"\\s+"," ",re.sub(r"<[^>]+>"," ",str(s or ""))).strip()[:500]

def normalize(source,lane,title,url,description="",published="",metrics=None):
    p=urllib.parse.urlsplit(url or "")
    if p.scheme!="https" or not p.hostname or p.username or p.password:
        return None
    return {"id":hashlib.sha256((source+"|"+url).encode()).hexdigest()[:16],
            "source":source,"lane":lane,"title":clean(title)[:180],"url":url,
            "description":clean(description),"published":str(published or "")[:60],
            "metrics":metrics or {},"status":"UNREVIEWED_LEAD",
            "ghostmesh_relevance":"UNKNOWN","outreach_authorized":False}

def xml_items(payload,source,lane,limit=8):
    root=ET.fromstring(payload)
    result=[]
    atom="{http://www.w3.org/2005/Atom}"
    nodes=root.findall(".//item") or root.findall(f".//{atom}entry")
    for node in nodes[:limit*3]:
        title=node.findtext("title") or node.findtext(atom+"title") or ""
        link=node.findtext("link") or ""
        if not link:
            for element in node.findall(atom+"link"):
                if element.get("rel","alternate")=="alternate":
                    link=element.get("href","");break
        if link.startswith("http://"): link="https://"+link[len("http://"):]
        desc=node.findtext("description") or node.findtext(atom+"summary") or ""
        published=node.findtext("pubDate") or node.findtext(atom+"published") or node.findtext(atom+"updated") or ""
        item=normalize(source,lane,title,link,desc,published)
        if item and item["title"]: result.append(item)
        if len(result)==limit: break
    return result

def github_items(query,payload,limit=7):
    result=[]
    for repo in json.loads(payload).get("items",[])[:limit]:
        item=normalize("github-search","code",repo.get("full_name"),repo.get("html_url"),
                       repo.get("description"),repo.get("pushed_at"),
                       {"stars":repo.get("stargazers_count"),"forks":repo.get("forks_count"),
                        "metric_scope":"repository cumulative, not trend velocity"})
        if item: result.append(item)
    return result

def hn_items(ids_payload,item_fetcher=fetch,limit=8):
    result=[]
    for story_id in json.loads(ids_payload)[:limit*2]:
        try:
            raw=item_fetcher(f"https://hacker-news.firebaseio.com/v0/item/{int(story_id)}.json")
            story=json.loads(raw)
            if not story or story.get("type")!="story":continue
            url=story.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
            item=normalize("hacker-news","attention",story.get("title"),url,
                           "HN discussion: https://news.ycombinator.com/item?id="+str(story_id),
                           story.get("time"),{"points":story.get("score"),"comments":story.get("descendants"),
                           "metric_scope":"single sampled ranking; no growth history"})
            if item: result.append(item)
            if len(result)>=limit:break
        except (ValueError,KeyError,TypeError,urllib.error.URLError):continue
    return result

def run(transport=fetch,cap=8):
    if not 1<=cap<=15:raise ValueError("cap must be 1..15")
    entries=[];diagnostics=[]
    for source,(url,lane) in FEEDS.items():
        try:
            found=xml_items(transport(url),source,lane,cap)
            entries+=found
            diagnostics.append({"source":source,"state":"FETCHED","items":len(found)})
        except Exception as error:
            diagnostics.append({"source":source,"state":"ERROR","error_type":type(error).__name__})
    for query in GITHUB_QUERIES:
        name="github:"+query
        url=API_GITHUB+"?"+urllib.parse.urlencode({"q":query,"sort":"updated","order":"desc","per_page":cap})
        try:
            found=github_items(query,transport(url),cap)
            entries+=found
            diagnostics.append({"source":name,"state":"FETCHED","items":len(found)})
        except Exception as error:
            diagnostics.append({"source":name,"state":"ERROR","error_type":type(error).__name__})
    try:
        found=hn_items(transport(HN_URL),transport,cap)
        entries+=found
        diagnostics.append({"source":"hacker-news","state":"FETCHED","items":len(found)})
    except Exception as error:
        diagnostics.append({"source":"hacker-news","state":"ERROR","error_type":type(error).__name__})
    seen=set();unique=[]
    for item in entries:
        canonical=item["url"].rstrip("/")
        if canonical in seen:continue
        seen.add(canonical);unique.append(item)
    return {"schema":"scout-multisource-intake-v0","captured_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "sampled_leads":unique,"diagnostics":diagnostics,
            "measurement_limits":["One-time feed snapshot, not independently measured virality",
                                  "Source metadata not checked against individual article bodies",
                                  "No social platform coverage claimed for Reddit, X, YouTube, Instagram or Bluesky",
                                  "Search terms are topic biased; not a representative discovery sample"],
            "publication_authorized":False,"outreach_authorized":False}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",required=True)
    ap.add_argument("--cap",type=int,default=6)
    a=ap.parse_args()
    from pathlib import Path
    path=Path(a.out)
    if path.exists():raise SystemExit("Refusing overwrite")
    payload=run(cap=a.cap)
    path.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"leads":len(payload["sampled_leads"]),"diagnostics":payload["diagnostics"],"output":str(path)},indent=2))
if __name__=="__main__":main()
