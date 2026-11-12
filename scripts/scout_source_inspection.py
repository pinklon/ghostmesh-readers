"""Source inspection gate: classify extraction sufficiency, not scientific truth."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from scout_receipt_report import report

def inspect(receipts: Path):
    report(receipts)  # verifies all original bytes and receipt hashes
    manifest=json.loads((receipts/"manifest.json").read_text(encoding="utf-8"))
    output=[]
    for item in manifest["results"]:
        if item["status"]!="FETCHED_UNVERIFIED":
            output.append({"id":item["id"],"source_url":item["source_url"],"status":"FETCH_FAILED"})
            continue
        packet=json.loads((receipts/(item["id"]+".json")).read_text(encoding="utf-8"))
        extracted=packet["substantive_text"]
        excerpt=extracted.get("excerpt") or ""
        # Conservative quality signal only: absence of meaningful text cannot be passed.
        sufficient=(extracted.get("extraction_status")=="EXTRACTED_UNVERIFIED"
                    and len(excerpt.split())>=35)
        output.append({"id":item["id"],"source_url":item["source_url"],
                       "title":extracted.get("title") or "UNTITLED",
                       "snapshot_sha256":packet["snapshot_sha256"],
                       "excerpt_words":len(excerpt.split()),
                       "extraction_quality":"REVIEWABLE_EXCERPT" if sufficient else "INSUFFICIENT_TEXT",
                       "claim_accuracy":"NOT_EVALUATED","originality":"NOT_EVALUATED",
                       "ghostmesh_relevance":"NOT_EVALUATED",
                       "limitations":"Word-count sufficiency is not relevance, novelty, or evidence of truth"})
    return {"schema":"scout-source-inspection-v0","cases":output,
            "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--receipts",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("No overwrites")
    out=inspect(a.receipts)
    a.out.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
