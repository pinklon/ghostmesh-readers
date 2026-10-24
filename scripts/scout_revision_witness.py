"""Scout source revision witness: distinguish immutable revisions from feed positions.

Research-only. This records upstream revision identifiers, not content significance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote,urlsplit

USER_AGENT="GhostMesh-Scout-Research/0.1"
REPO=re.compile(r"^/([^/]+)/([^/]+)/?$")
ARXIV_ID=re.compile(r"^/abs/(\d{4}\.\d{4,5})(?:v(\d+))?/?$")
ARXIV_VERSION=re.compile(r"/abs/\d{4}\.\d{4,5}v(\d+)")

def identify(url):
    p=urlsplit(url)
    if p.scheme!="https" or p.username or p.password or p.port not in (None,443):
        raise ValueError("public HTTPS only")
    if p.hostname=="github.com":
        match=REPO.fullmatch(p.path)
        if match:return ("github",match.group(1),match.group(2))
    if p.hostname=="arxiv.org":
        match=ARXIV_ID.fullmatch(p.path)
        if match:return ("arxiv",match.group(1),None)
    raise ValueError("Unsupported source identity")

def _read(url,transport=None):
    if transport:return transport(url)
    request=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json,text/html"})
    with urllib.request.urlopen(request,timeout=8) as r:
        if r.status!=200:raise ValueError("Unexpected upstream response")
        data=r.read(500001)
        if len(data)>500000:raise ValueError("Oversized upstream response")
        return data

def witness(url,transport=None):
    kind,a,b=identify(url)
    if kind=="github":
        endpoint="https://api.github.com/repos/"+quote(a,safe="")+"/"+quote(b,safe="")
        repo=json.loads(_read(endpoint,transport))
        branch=repo.get("default_branch")
        if not isinstance(branch,str) or not branch:raise ValueError("No default branch")
        commit=json.loads(_read(endpoint+"/commits/"+quote(branch,safe=""),transport))
        revision=commit.get("sha")
        if not isinstance(revision,str) or not re.fullmatch(r"[a-fA-F0-9]{40}",revision):
            raise ValueError("No verified commit identifier")
        return {"source_url":url,"kind":"github","identity":a+"/"+b,"revision":revision.lower(),
                "revision_basis":"GitHub REST default branch commit SHA",
                "stable_content_url":"https://github.com/"+a+"/"+b+"/tree/"+revision.lower(),
                "content_review":"NOT_PERFORMED"}
    html=_read("https://arxiv.org/abs/"+a,transport).decode("utf-8",errors="replace")
    # arXiv exposes a permanent linked paper history. Parse only revision hyperlinks,
    # not manuscript dates or a feed-entry timestamp.
    versions=[int(x) for x in ARXIV_VERSION.findall(html)]
    if not versions:raise ValueError("No explicit arXiv revision found")
    version=max(versions)
    return {"source_url":url,"kind":"arxiv","identity":a,"revision":"v"+str(version),
            "revision_basis":"arxiv.org abstract page version references",
            "stable_content_url":"https://arxiv.org/abs/"+a+"v"+str(version),
            "content_review":"NOT_PERFORMED"}

def compare(before,after):
    if before["identity"]!=after["identity"] or before["kind"]!=after["kind"]:
        raise ValueError("Different works cannot be compared")
    state="REVISION_ID_CHANGED" if before["revision"]!=after["revision"] else "SAME_REVISION_ID"
    return {"identity":after["identity"],"kind":after["kind"],"before":before["revision"],
            "after":after["revision"],"state":state,"substantive_change":"NOT_ASSESSED",
            "note":"Revision ID change is not evidence of a meaningful content change"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url",action="append",required=True)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    if args.out.exists():raise SystemExit("Refuse overwrite")
    records=[]; errors=[]
    for url in args.url:
        try:records.append(witness(url))
        except Exception as e:errors.append({"source_url":url,"error_type":type(e).__name__})
    result={"schema":"scout-revision-witness-v0","captured_utc":datetime.now(timezone.utc).isoformat(),
            "records":records,"errors":errors,"publication_authorized":False,
            "outreach_authorized":False}
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"witnesses":len(records),"errors":errors},indent=2))
    if errors:raise SystemExit(1)

if __name__=="__main__":main()
