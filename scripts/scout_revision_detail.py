"""Scout revision detail: read-only upstream commit file lists and paper text changes.

This does not claim a source change has overturned any GhostMesh conclusion.
"""
from __future__ import annotations
import argparse
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import quote

SHA=re.compile(r"^[0-9a-f]{40}$")
ARXIV=re.compile(r"^\d{4}\.\d{4,5}$")
def read(url,transport=None):
    if transport:return transport(url)
    req=urllib.request.Request(url,headers={"User-Agent":"GhostMesh-Scout-Research/0.1","Accept":"application/vnd.github+json,text/html"})
    with urllib.request.urlopen(req,timeout=8) as response:
        if response.status!=200:raise ValueError("Unexpected upstream response")
        data=response.read(700001)
        if len(data)>700000:raise ValueError("Oversized upstream comparison")
        return data

def github_changes(owner,repo,before,after,transport=None):
    if not (all(re.fullmatch(r"[A-Za-z0-9_.-]{1,100}",s) for s in (owner,repo))
            and SHA.fullmatch(before) and SHA.fullmatch(after)):
        raise ValueError("Invalid repository or exact commit IDs")
    url=f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}/compare/{before}...{after}"
    data=json.loads(read(url,transport))
    files=data.get("files",[])
    if not isinstance(files,list):raise ValueError("Missing changed files")
    out=[]
    for f in files[:100]:
        out.append({"path":str(f.get("filename",""))[:300],"status":f.get("status"),
                    "additions":f.get("additions"),"deletions":f.get("deletions"),
                    "patch_available":isinstance(f.get("patch"),str),
                    "patch_excerpt":str(f.get("patch",""))[:1200]})
    return {"schema":"scout-github-change-evidence-v0","identity":owner+"/"+repo,
            "before_revision":before,"after_revision":after,
            "provider_status":data.get("status"),"provider_ahead_by":data.get("ahead_by"),
            "files":out,"files_truncated":len(files)>100,
            "semantic_significance":"NOT_EVALUATED","thesis_impact":"NOT_EVALUATED",
            "publication_authorized":False,"outreach_authorized":False}

def arxiv_text(arxiv_id,version,transport=None):
    if not ARXIV.fullmatch(arxiv_id) or not re.fullmatch(r"v[1-9]\d*",version):
        raise ValueError("Invalid arXiv revision")
    url=f"https://arxiv.org/html/{arxiv_id}{version}"
    data=read(url,transport)
    from scout_html_extract import extract
    parsed=extract(data.decode("utf-8",errors="replace"))
    return {"source_url":url,"revision":version,"extraction":parsed,
            "text_review":"NOT_EVALUATED","content_scope":"EXTRACTED_EXCERPT_NOT_FULL_PAPER"}

def possible_reassessment(change, assessments):
    """Only signal need for review when changed source identity matches a prior assessment."""
    if not isinstance(assessments,list):raise ValueError("Assessment list required")
    out=[]
    changed=change.get("before_revision")!=change.get("after_revision")
    for assessment in assessments:
        if assessment.get("source_identity")==change.get("identity") and changed:
            out.append({"assessment_id":assessment.get("id"),
                        "state":"REASSESSMENT_CANDIDATE",
                        "reason":"New upstream revision for cited source",
                        "conclusion_overturned":False})
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--github",nargs=4,metavar=("OWNER","REPO","BEFORE_SHA","AFTER_SHA"))
    p.add_argument("--arxiv",nargs=2,metavar=("PAPER_ID","VERSION"))
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if bool(a.github)==bool(a.arxiv):raise SystemExit("Supply exactly one source")
    if a.out.exists():raise SystemExit("Refusing overwrite")
    result=github_changes(*a.github) if a.github else arxiv_text(*a.arxiv)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"schema":result.get("schema"),"files":len(result.get("files",[])),
                      "version":result.get("revision"),"out":str(a.out)}))
if __name__=="__main__": main()
