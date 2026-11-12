"""Persistent, owner-private Scout ledger replay with explicit retry receipts.

Consumes already captured observation/failure records. Does not fetch sources,
start services, mutate existing collector state, or retry network operations.
Writes state atomically only after validating the complete batch.
"""
from __future__ import annotations
import argparse
import json
import os
import tempfile
from pathlib import Path
from scout_ingestion_ledger import record_ledger, identity_revision

SCHEMA="scout-persistent-ingestion-state-v0"
ALLOWED_ERRORS={"HTTP_TIMEOUT","HTTP_429","HTTP_5XX","PARSE_ERROR","SOURCE_UNAVAILABLE","RETRIEVAL_ERROR"}
def empty_state():
    return {"schema":SCHEMA,"seen_keys":[],"pending":[],"runs":0,
            "publication_authorized":False,"outreach_authorized":False}

def validate_state(state):
    if state.get("schema")!=SCHEMA or state.get("publication_authorized") is not False or state.get("outreach_authorized") is not False:
        raise ValueError("Invalid research-only state")
    keys=state.get("seen_keys")
    if not isinstance(keys,list) or len({tuple(x) for x in keys})!=len(keys):
        raise ValueError("Invalid or repeated seen keys")
    for key in keys:
        if not isinstance(key,list) or len(key)!=2 or not all(isinstance(x,str) and x for x in key):
            raise ValueError("Malformed revision key")
    if not isinstance(state.get("runs"),int) or state["runs"]<0:
        raise ValueError("Invalid run count")
    if not isinstance(state.get("pending"),list):
        raise ValueError("Invalid pending queue")
    for p in state["pending"]:
        if not isinstance(p,dict) or set(p)!={"url","error_code","attempts"}:
            raise ValueError("Invalid pending entry")
        identity_revision(p["url"])
        if p["error_code"] not in ALLOWED_ERRORS or type(p["attempts"]) is not int or not 1<=p["attempts"]<=100:
            raise ValueError("Invalid pending attempt")
    return state

def process(state,batch):
    validate_state(state)
    if batch.get("schema")!="scout-ingestion-attempt-batch-v0" or batch.get("publication_authorized") is not False or batch.get("outreach_authorized") is not False:
        raise ValueError("Invalid batch authority")
    observations=batch.get("attempts")
    if not isinstance(observations,list):
        raise ValueError("Missing attempt list")
    prior={p["url"]:dict(p) for p in state["pending"]}
    good=[];failure_receipts=[]
    for i,item in enumerate(observations):
        if not isinstance(item,dict) or item.get("status") not in {"SUCCESS","FAILED"}:
            raise ValueError("Invalid attempt status")
        url=item.get("url")
        identity_revision(url)
        if item["status"]=="SUCCESS":
            if item.get("error_code") is not None:
                raise ValueError("Success cannot include error")
            obs={k:v for k,v in item.items() if k!="status"}
            good.append(obs)
            prior.pop(url,None)
        else:
            if set(item)-{"url","status","error_code"} or item.get("error_code") not in ALLOWED_ERRORS:
                raise ValueError("Unrecognized failure event")
            past=prior.get(url)
            count=1+(past["attempts"] if past else 0)
            if count>100:raise ValueError("Retry limit reached")
            prior[url]={"url":url,"error_code":item["error_code"],"attempts":count}
            failure_receipts.append({"index":i,"url":url,"state":"DEFERRED_RETRY",
                    "error_code":item["error_code"],"attempts":count,
                    "source_content_verified":False,"outreach_authorized":False})
    result=record_ledger(good,state["seen_keys"])
    next_state={"schema":SCHEMA,"seen_keys":result["seen_keys"],"pending":sorted(prior.values(),key=lambda x:x["url"]),
                "runs":state["runs"]+1,"publication_authorized":False,"outreach_authorized":False}
    report={"schema":"scout-persistent-ingestion-run-v0",
            "run_number":next_state["runs"],"accepted":result["accepted"],
            "duplicate_revisions":result["duplicates"],
            "unverified_reobservations":result["unverified_reobservations"],
            "deferred":len(failure_receipts),"pending_after":len(next_state["pending"]),
            "source_receipts":result["receipts"],"failure_receipts":failure_receipts,
            "state_written":False,"publication_authorized":False,"outreach_authorized":False,
            "limits":["Retries are queued, not automatically executed","Failed captures never advance revision state",
                      "Unknown revisions may have changed","No identity matching or public action"]}
    return next_state,report

def atomic_json(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=".scout-ledger-",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as out:
            json.dump(content,out,indent=2,ensure_ascii=False)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--batch",type=Path,required=True)
    p.add_argument("--state",type=Path,required=True)
    p.add_argument("--receipt",type=Path,required=True)
    a=p.parse_args()
    if a.receipt.exists():raise SystemExit("Receipt exists; refusing overwrite")
    if a.state.resolve()==a.receipt.resolve():raise SystemExit("Receipt and state must differ")
    state=validate_state(json.loads(a.state.read_text(encoding="utf-8"))) if a.state.exists() else empty_state()
    batch=json.loads(a.batch.read_text(encoding="utf-8"))
    next_state,report=process(state,batch)
    # Receipt is a separate private artifact. If its write fails, previous state
    # is untouched. Recovery can replay the same batch idempotently.
    atomic_json(a.receipt,report)
    atomic_json(a.state,next_state)
    print(json.dumps({k:report[k] for k in ("run_number","accepted","duplicate_revisions","unverified_reobservations","deferred","pending_after")},indent=2))
if __name__=="__main__":main()
