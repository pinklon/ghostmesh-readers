"""Bounded public trail discovery for Scout authors and GitHub account handles.

Search arXiv author strings and public GitHub account-owned repositories. Results
are research clues, NOT cross-platform identity verification or collaborator leads.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ATOM="{http://www.w3.org/2005/Atom}"
MAX_BYTES=1500000
def fetch(url,transport=None):
    if transport:return transport(url)
    req=urllib.request.Request(url,headers={"User-Agent":"GhostMesh-Scout-Research/0.1","Accept":"application/json,application/atom+xml"})
    with urllib.request.urlopen(req,timeout=8) as resp:
        if resp.status!=200:raise ValueError("Bad response")
        raw=resp.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError("Source too large")
        return raw

def arxiv_trail(name,initial_url,transport=None,limit=4):
    if not isinstance(name,str) or len(name)>100 or not re.fullmatch(r"[\w .'-]+",name,re.UNICODE):
        raise ValueError("Invalid author-label query")
    query=urllib.parse.quote('au:"'+name+'"')
    url="https://export.arxiv.org/api/query?search_query="+query+"&start=0&max_results="+str(limit)
    root=ET.fromstring(fetch(url,transport))
    findings=[]
    for item in root.findall(ATOM+"entry")[:limit]:
        src=(item.findtext(ATOM+"id") or "").strip()
        match=re.search(r"arxiv.org/abs/(\d{4}\.\d{4,5})(?:v\d+)?",src)
        if not match:continue
        paper="https://arxiv.org/abs/"+match.group(1)
        names=[" ".join((a.findtext(ATOM+"name") or "").split()) for a in item.findall(ATOM+"author")]
        if name.casefold() not in (n.casefold() for n in names):continue
        title=" ".join((item.findtext(ATOM+"title") or "").split())[:250]
        if paper.rstrip("/")==re.sub(r'v\d+$','',initial_url.rstrip("/")):continue
        findings.append({"kind":"arxiv_exact_byline_match","label":name,"work_url":paper,"work_title":title,
            "support":"Exact author-name string reappears in arXiv record; may be a namesake",
            "same_real_person_confirmed":False,"contact_authorized":False})
    return findings

def github_trail(handle,origin,transport=None,limit=5):
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}",handle):raise ValueError("Invalid handle")
    url="https://api.github.com/users/"+handle+"/repos?per_page="+str(limit)+"&sort=updated&type=owner"
    payload=json.loads(fetch(url,transport))
    if not isinstance(payload,list):raise ValueError("Non-list GitHub result")
    rows=[]
    for repo in payload[:limit]:
        if not isinstance(repo,dict):continue
        if repo.get("private") is not False or repo.get("fork") is True:continue
        owner=repo.get("owner") or {}
        if owner.get("login","").casefold()!=handle.casefold():continue
        web=repo.get("html_url","")
        if not isinstance(web,str) or not re.fullmatch(r"https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+",web):continue
        if web.rstrip("/").casefold()==origin.rstrip("/").casefold():continue
        rows.append({"kind":"github_same_account_repository","label":handle,
            "work_url":web,"work_title":repo.get("full_name","")[:220],
            "description":str(repo.get("description") or "")[:400],
            "support":"Repository publicly owned by the same GitHub account handle",
            "same_real_person_confirmed":False,"contact_authorized":False})
    return rows

def collect(entries,transport=None,max_per_kind=3):
    if entries.get("schema")!="scout-work-first-discovery-v0" or entries.get("publication_authorized") is not False or entries.get("outreach_authorized") is not False:
        raise ValueError("Private attribution input required")
    trails=[];coverage=[];selected={"public_author_name":0,"github_account_handle":0}
    for item in entries.get("entries",[]):
        kind=item.get("kind")
        if kind not in selected or selected[kind]>=max_per_kind:continue
        selected[kind]+=1
        label=item.get("label","");origin=item.get("work_url","")
        try:
            if kind=="public_author_name":found=arxiv_trail(label,origin,transport)
            else:found=github_trail(label,origin,transport)
            coverage.append({"label":label,"source_kind":kind,"status":"FETCHED","trail_count":len(found)})
            for record in found:
                record["origin_work"]=origin
                record["id"]=hashlib.sha256((kind+"|"+label+"|"+record["work_url"]).encode()).hexdigest()[:18]
                trails.append(record)
        except Exception as ex:
            coverage.append({"label":label,"source_kind":kind,"status":"ERROR","error_type":type(ex).__name__})
    return {"schema":"scout-public-contribution-trails-v0","trails":trails,"coverage":coverage,
        "selection":"First three eligible public attributions per kind, fixed input order; convenience sample only",
        "limits":["Matching paper bylines do not disambiguate people",
                  "Same GitHub account ownership does not establish expertise, originality or collaboration interest",
                  "Never merge arXiv names with GitHub accounts without independent evidence",
                  "Search endpoint ordering and bounded results are not exhaustive"],
        "identity_verified":False,"outreach_authorized":False,"publication_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse overwrite")
    report=collect(json.loads(a.source.read_text(encoding="utf-8")))
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"trails":len(report["trails"]),"coverage":report["coverage"]},indent=2))
if __name__=="__main__":main()
