"""Reconcile Scout claim source pins against upstream revision witnesses.

Flags claims needing review; never automatically edits a conclusion or claims a scientific result.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

VALID={"INVESTIGATE","FOLLOW","NO_CONNECTION_JUSTIFIED","ARCHIVE"}
def evaluate(register:dict, witness:dict)->dict:
    if register.get("schema")!="scout-claim-register-v0" or witness.get("schema")!="scout-revision-witness-v0":
        raise ValueError("Unexpected input schema")
    for obj in (register,witness):
        if obj.get("outreach_authorized") is not False or obj.get("publication_authorized") is not False:
            raise ValueError("No outreach or public authority")
    by_key={}
    for item in witness.get("records",[]):
        key=(item.get("kind"),item.get("identity"))
        if key in by_key:raise ValueError("Ambiguous revisions for source")
        by_key[key]=item
    results=[];ids=set()
    for claim in register.get("claims",[]):
        cid=claim["id"]
        if cid in ids:raise ValueError("Duplicate claim")
        ids.add(cid)
        if claim.get("disposition") not in VALID:raise ValueError("Invalid disposition")
        if not claim.get("source_revision") or not claim.get("source_identity"):
            raise ValueError("Unpinned source")
        if urlsplit(claim.get("source_url","")).scheme!="https":raise ValueError("Source URL must be HTTPS")
        observed=by_key.get((claim["source_kind"],claim["source_identity"]))
        if observed is None:
            state="NO_CURRENT_WITNESS"
        elif observed.get("revision")==claim["source_revision"]:
            state="REVISION_MATCH"
        else:
            state="REVIEW_SOURCE_REVISION"
        results.append({"claim_id":cid,"source_identity":claim["source_identity"],
            "source_kind":claim["source_kind"],"pinned_revision":claim["source_revision"],
            "observed_revision":observed.get("revision") if observed else None,
            "state":state,"editorial_disposition":claim["disposition"],
            "disposition_changed":False,"source_claim_validity":"NOT_REPRODUCED",
            "recommended_action":"COMPARE_CHANGED_CONTENT" if state=="REVIEW_SOURCE_REVISION" else
                                 "OBTAIN_REVISION_WITNESS" if state=="NO_CURRENT_WITNESS" else "NO_REVISION_TRIGGER"})
    return {"schema":"scout-claim-impact-v0","observations":results,
        "counts":{"claims":len(results),"matched":sum(x["state"]=="REVISION_MATCH" for x in results),
            "revision_review":sum(x["state"]=="REVIEW_SOURCE_REVISION" for x in results),
            "without_witness":sum(x["state"]=="NO_CURRENT_WITNESS" for x in results)},
        "limits":["Revision match does not verify authors' empirical claims",
                  "Revision change cannot by itself overturn a conclusion",
                  "A new revision requires content-level comparison before assessing impact"],
        "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--register",type=Path,required=True)
    p.add_argument("--witness",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise SystemExit("Refusing to overwrite report")
    read=lambda x:json.loads(x.read_text(encoding="utf-8"))
    result=evaluate(read(args.register),read(args.witness))
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result["counts"],indent=2))
if __name__=="__main__":main()
