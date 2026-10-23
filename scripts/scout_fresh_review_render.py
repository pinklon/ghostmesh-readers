"""Render a reviewer packet directly from a frozen Scout experiment JSON.

The packet embeds an SHA-256 receipt for its exact case data. No model runs,
no access to the sealed cohort key, and no inference about source merit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def canonical_hash(packet):
    return hashlib.sha256(json.dumps(packet,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()

def render(packet):
    if packet.get("schema")!="scout-fresh-blind-review-v0" or packet.get("publication_authorized") is not False or packet.get("outreach_authorized") is not False:
        raise ValueError("Private fresh blind review required")
    cards=packet.get("cards")
    if not isinstance(cards,list) or not 1<=len(cards)<=30 or len(cards)!=packet.get("case_count"):
        raise ValueError("Invalid frozen case count")
    ids=[x.get("review_id") for x in cards]
    if len(set(ids))!=len(ids) or len(set(x.get("source_url") for x in cards))!=len(cards):
        raise ValueError("Repeated review ID or source")
    if [x.get("sequence") for x in cards]!=list(range(1,len(cards)+1)):
        raise ValueError("Unstable review ordering")
    for card in cards:
        if not all(isinstance(card.get(key),str) and card[key].strip() for key in ("review_id","title","source_url","source_excerpt")):
            raise ValueError("Incomplete case")
        if not card["source_url"].startswith("https://") or any(key in card for key in ("cohort","prior_verdict","known_relevance")):
            raise ValueError("Private cohort leakage or invalid source")
        if card.get("relevance") is not None or card.get("novelty") is not None or card.get("surprise") is not None:
            raise ValueError("Do not publish scored cases as blind")
    digest=canonical_hash(packet)
    h=["# Scout | Fresh independent discovery review\n",
       "**Owner-private research only. No outreach, merge, or production action.**\n",
       "Frozen packet SHA-256: `"+digest+"`. This value attests to the JSON case data, not external source validity.\n",
       "## Reviewer rules\n",
       "Assess every case on the same budget ceiling: 5 minutes and 1 primary-source open. "
       "Rate relevance 0–3 or ABSTAIN; novelty and surprise 0–2 or ABSTAIN. "
       "Record whether the source was opened, the strongest objection, and a source-grounded rationale. "
       "Do not look up the sealed cohort map, earlier verdicts, or prior experiments before finalizing. "
       "An inaccessible source is not a negative relevance finding.\n",
       "The packet contains titles and feed excerpts that are **unverified metadata**. "
       "Blinding withholds cohort labels and prior scores, not evidence of authorship or topic.\n"]
    for c in cards:
        h.extend(["### "+str(c["sequence"])+". "+c["review_id"]+"\n",
            "**Title:** "+c["title"].replace("\n"," ")+"\n",
            "**Primary source:** "+c["source_url"]+"\n",
            "**Unverified feed excerpt:** "+c["source_excerpt"].replace("\n"," ")+"\n",
            "**Assessment:** relevance ___ · novelty ___ · surprise ___ · source inspected ___\n",
            "**Strongest objection:** ___\n",
            "**Rationale / evidence limitations:** ___\n",
            "---\n"])
    h.append("Return all "+str(len(cards))+" IDs with documented abstentions. No source or contributor contact is authorized.\n")
    return "\n".join(h)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--packet",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    packet=json.loads(a.packet.read_text(encoding="utf-8"))
    a.out.write_text(render(packet),encoding="utf-8")
    print(json.dumps({"case_count":packet["case_count"],"packet_sha256":canonical_hash(packet),"output":str(a.out)}))
if __name__=="__main__":main()
