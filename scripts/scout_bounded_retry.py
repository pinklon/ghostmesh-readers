"""One-shot, bounded pending-source retry runner for Scout research.

Reads persisted pending entries, calls the existing allowlisted public collector
at most once per eligible source, and writes an explicit replay batch/receipt.
No timer, background service, auth tokens, publication, or outreach.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import urllib.error
from pathlib import Path
from scout_persistent_ledger import validate_state,process,atomic_json,ALLOWED_ERRORS
from scout_source_collector import collect,HOSTS
from urllib.parse import urlsplit

MAX_PER_RUN=3
MAX_TOTAL_ATTEMPTS=3
def safe_url(url):
    if not isinstance(url,str):raise ValueError("Missing pending URL")
    p=urlsplit(url)
    if (p.scheme!="https" or p.hostname not in HOSTS or p.port not in (None,443)
        or p.username or p.password or p.fragment):
        raise ValueError("Pending source outside permitted collector hosts")
    return url

def error_code(exc):
    if isinstance(exc,urllib.error.HTTPError):
        return "HTTP_429" if exc.code==429 else "HTTP_5XX" if 500<=exc.code<=599 else "SOURCE_UNAVAILABLE"
    if isinstance(exc,(TimeoutError,urllib.error.URLError)):
        return "HTTP_TIMEOUT"
    if isinstance(exc,(UnicodeError,json.JSONDecodeError)):
        return "PARSE_ERROR"
    return "RETRIEVAL_ERROR"

def execute(state,collector=collect,max_sources=MAX_PER_RUN):
    validate_state(state)
    if type(max_sources) is not int or not 1<=max_sources<=MAX_PER_RUN:
        raise ValueError("Invalid bounded retry count")
    # Validate the complete pending queue *before* calling external sources.
    pending=sorted(state["pending"],key=lambda x:x["url"])
    for item in pending:safe_url(item["url"])
    attempts=[];exhausted=[]
    for item in pending:
        if item["attempts"]>=MAX_TOTAL_ATTEMPTS:
            exhausted.append({"url":item["url"],"state":"EXHAUSTED_REVIEW_REQUIRED",
                              "attempts":item["attempts"],"outreach_authorized":False})
            continue
        if len(attempts)>=max_sources:break
        url=item["url"]
        try:
            digest=None
            def snapshot(raw):
                nonlocal digest
                digest=hashlib.sha256(raw).hexdigest()
            collector(url,snapshot_callback=snapshot)
            if digest is None:raise ValueError("Collector supplied no captured bytes")
            attempts.append({"url":url,"status":"SUCCESS","capture_sha256":digest})
        except Exception as exc:
            attempts.append({"url":url,"status":"FAILED","error_code":error_code(exc)})
    batch={"schema":"scout-ingestion-attempt-batch-v0","attempts":attempts,
           "publication_authorized":False,"outreach_authorized":False}
    next_state,report=process(state,batch)
    report["retry_execution"]={"attempted":len(attempts),"max_sources":max_sources,
         "exhausted":exhausted,"pending_not_attempted":sum(
            x["attempts"]<MAX_TOTAL_ATTEMPTS for x in pending)-len(attempts),
         "automatic_future_retry":False,"external_actions":"ALLOWLISTED_PUBLIC_READ_ONLY_GET"}
    return next_state,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--state",required=True,type=Path)
    p.add_argument("--receipt",required=True,type=Path)
    p.add_argument("--max-sources",type=int,default=MAX_PER_RUN)
    p.add_argument("--apply",action="store_true",help="Persist new private state and receipt")
    a=p.parse_args()
    state=validate_state(json.loads(a.state.read_text(encoding="utf-8")))
    if not a.apply:
        print(json.dumps({"mode":"DRY_RUN","eligible":sum(
            x["attempts"]<MAX_TOTAL_ATTEMPTS for x in state["pending"]),
            "exhausted":sum(x["attempts"]>=MAX_TOTAL_ATTEMPTS for x in state["pending"]),
            "maximum_sources":min(a.max_sources,MAX_PER_RUN),
            "network_calls":0},indent=2))
        return
    if a.receipt.exists() or a.receipt.resolve()==a.state.resolve():
        raise SystemExit("Refusing to overwrite existing receipt or state path collision")
    next_state,report=execute(state,max_sources=a.max_sources)
    # A receipt records intent/results; state is then atomically replaced.
    # Existing process() semantics make replay idempotent for revisions,
    # but a crash between writes needs explicit operator reconciliation.
    atomic_json(a.receipt,report)
    atomic_json(a.state,next_state)
    print(json.dumps({"attempted":report["retry_execution"]["attempted"],
                      "accepted":report["accepted"],"deferred":report["deferred"],
                      "pending":report["pending_after"],
                      "exhausted":len(report["retry_execution"]["exhausted"])},indent=2))
if __name__=="__main__":main()
