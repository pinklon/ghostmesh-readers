"""Validate independent Scout review receipts without accessing sealed cohorts."""
import argparse,json,re
from pathlib import Path

def verify(packet,review,expected_blob):
    if packet.get("schema")!="scout-blind-review-packet-v0":raise ValueError("Packet schema")
    if review.get("schema")!="scout-independent-review-labels-v0":raise ValueError("Rating schema")
    if not re.fullmatch("[a-f0-9]{40}",expected_blob):raise ValueError("Blob hash")
    if review.get("packet",{}).get("git_blob_sha")!=expected_blob:raise ValueError("Wrong packet revision")
    ids=[x["review_id"] for x in packet["cards"]]
    ratings=review.get("ratings",[])
    if len(ids)!=21 or len(set(ids))!=21 or len(ratings)!=21:raise ValueError("21 cases required")
    if {r.get("review_id") for r in ratings}!=set(ids):raise ValueError("Missing or duplicate case")
    totals={"0":0,"1":0,"2":0,"3":0,"ABSTAIN":0}
    checked=0
    for row in ratings:
        val=row.get("ghostmesh_relevance")
        if type(val) is int:val=str(val)
        if val not in totals:raise ValueError("Invalid relevance")
        totals[val]+=1
        for name in ("novelty","surprise"):
            v=row.get(name)
            if v!="ABSTAIN" and (type(v) is not int or v not in (0,1,2)):
                raise ValueError("Invalid "+name)
        if type(row.get("primary_source_inspected")) is not bool:raise ValueError("Missing source witness")
        checked+=int(row["primary_source_inspected"])
        for name in ("rationale","strongest_objection","source_review_sufficiency"):
            if not isinstance(row.get(name),str) or len(row[name].strip())<12:raise ValueError("Missing rationale")
        n=row.get("additional_source_opens")
        if type(n) is not int or n not in (0,1):raise ValueError("Budget violation")
    return {"schema":"scout-review-integrity-v0","packet_blob":expected_blob,
            "cases":21,"relevance":totals,"source_inspected":checked,
            "cohort_unsealed":False,"conclusion":"STRUCTURAL_VALIDITY_ONLY",
            "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser()
    for name in ("packet","review","out"):p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--packet-blob",required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    data=verify(json.loads(a.packet.read_text()),json.loads(a.review.read_text()),a.packet_blob)
    a.out.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data))
if __name__=="__main__":main()
