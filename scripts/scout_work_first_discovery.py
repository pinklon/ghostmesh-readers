"""Scout work-first public creator discovery. Never equate a handle with a person.

Two narrow surfaces: arXiv RSS listed authors and GitHub public contributor handles.
No automated outreach, identity resolution, follower-based rank, or private account access.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

DC_CREATOR="{http://purl.org/dc/elements/1.1/}creator"
MAX_BYTES=2_500_000
def get(url,transport=None):
    if transport:return transport(url)
    req=urllib.request.Request(url,headers={"User-Agent":"GhostMesh-Scout-Research/0.1",
                                              "Accept":"application/json,application/rss+xml"})
    with urllib.request.urlopen(req,timeout=8) as response:
        if response.status!=200:raise ValueError("Unexpected status")
        data=response.read(MAX_BYTES+1)
        if len(data)>MAX_BYTES:raise ValueError("Oversized response")
        return data

def arxiv_creators(xml: bytes, limit=10):
    if len(xml)>MAX_BYTES:raise ValueError("Oversized RSS")
    root=ET.fromstring(xml)
    out=[]
    for item in root.findall(".//item")[:limit]:
        paper=item.findtext("link","")
        if not re.fullmatch(r"https://arxiv\.org/abs/\d{4}\.\d{4,5}(?:v\d+)?",paper):continue
        authors=item.findtext(DC_CREATOR,"")
        # Comma-separated creator metadata is not a verified identity authority.
        for raw in authors.split(",")[:12]:
            name=" ".join(raw.strip().split())
            if len(name)<3 or len(name)>120:continue
            out.append({"kind":"public_author_name","label":name,
                        "work_url":paper,"work_title":item.findtext("title","")[:220],
                        "basis":"arXiv RSS dc:creator field",
                        "identity_verified":False,"contact_authorized":False})
    return out

def github_contributors(owner,repo,transport=None,limit=8):
    if not all(re.fullmatch(r"[A-Za-z0-9_.-]{1,100}",x) for x in (owner,repo)):
        raise ValueError("Invalid GitHub repository")
    url=f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}/contributors?per_page={min(limit,20)}&anon=0"
    out=[]
    for item in json.loads(get(url,transport))[:limit]:
        login=item.get("login")
        if not isinstance(login,str) or not re.fullmatch(r"[A-Za-z0-9-]{1,39}",login):continue
        if item.get("type")!="User":continue
        out.append({"kind":"github_account_handle","label":login,
                    "work_url":f"https://github.com/{owner}/{repo}",
                    "account_url":f"https://github.com/{login}",
                    "basis":"GitHub public contributor endpoint; contribution count not a relevance score",
                    "identity_verified":False,"contact_authorized":False})
    return out

def build(arxiv:bytes, repos:list[tuple[str,str]],transport=None,limit=8):
    entries=arxiv_creators(arxiv,limit=limit)
    coverage=[{"source":"arxiv","status":"FETCHED","entries":len(entries)}]
    for owner,repo in repos:
        try:
            batch=github_contributors(owner,repo,transport,limit)
            entries.extend(batch)
            coverage.append({"source":owner+"/"+repo,"status":"FETCHED","entries":len(batch)})
        except Exception as ex:
            coverage.append({"source":owner+"/"+repo,"status":"ERROR","error_type":type(ex).__name__})
    # Names are NOT merged across papers or with account handles; only exact work+label repeats collapse.
    seen=set();unique=[]
    for e in entries:
        key=(e["kind"],e["label"],e["work_url"])
        if key in seen:continue
        seen.add(key)
        e["id"]=hashlib.sha256("|".join(key).encode()).hexdigest()[:18]
        unique.append(e)
    return {"schema":"scout-work-first-discovery-v0","entries":unique,"coverage":coverage,
        "limits":["Attribution metadata is not independently verified identity",
                  "GitHub contributors can include incidental edits; not necessarily maintainers",
                  "arXiv creators are paper metadata, not proof of independent originality",
                  "No followers, virality, inferred contact relationship or outreach"],
        "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arxiv-rss",required=True,type=Path)
    p.add_argument("--repo",action="append",default=[],help="public owner/repository")
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    if args.out.exists():raise SystemExit("Refusing overwrite")
    repos=[]
    for name in args.repo:
        bits=name.split("/")
        if len(bits)!=2:raise SystemExit("Expected owner/repository")
        repos.append(tuple(bits))
    result=build(args.arxiv_rss.read_bytes(),repos)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"discovered_work_attributions":len(result["entries"]),
                      "coverage":result["coverage"]},indent=2))
if __name__=="__main__":main()
