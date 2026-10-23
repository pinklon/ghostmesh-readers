"""Prepare an unbiased, fixed-effort Scout discovery review packet.

Candidate order is seeded and reviewer-facing metadata hides cohort, source feed,
engagement metrics, prior verdicts, and any previous editorial commentary.
Sealed map stays owner-private and scoring is by opaque ID. No labels are made up.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
from pathlib import Path

SCHEMA="scout-blind-review-packet-v0"
SEED="ghostmesh-scout-review-20261023-v1"
REQUIRED=("url","title")
def make_packet(intake, triage, outside):
    for obj, schema in ((intake,"scout-multisource-intake-v0"),
                        (triage,"scout-relevance-triage-v0"),
                        (outside,"scout-outside-bubble-v0")):
        if obj.get("schema")!=schema or obj.get("publication_authorized") is not False or obj.get("outreach_authorized") is not False:
            raise ValueError("Unexpected or unauthorized input")
    intake_map={}
    for lead in intake["sampled_leads"]:
        if any(not isinstance(lead.get(k),str) or not lead[k] for k in REQUIRED):raise ValueError("Missing lead metadata")
        if lead["url"] in intake_map:raise ValueError("Duplicate intake URL")
        intake_map[lead["url"]]=lead
    tagged={r["url"]:r for r in triage["entries"] if r.get("topics")}
    outside_map={r["url"]:r for r in outside["outside_sample"]}
    if set(tagged)&set(outside_map):raise ValueError("Cohorts must be disjoint")
    if not set(tagged|outside_map).issubset(intake_map):raise ValueError("Unknown candidate")
    if len(tagged)!=outside["topic_matched"] or len(outside_map)!=outside["outside_sampled"]:
        raise ValueError("Unexpected cohort coverage")
    mapping=[]
    for cohort,selection in (("TOPIC_MATCHED",tagged),("OUTSIDE_BUBBLE",outside_map)):
        for url in selection:
            lead=intake_map[url]
            opaque="SC-"+hashlib.sha256((SEED+"|"+url).encode()).hexdigest()[:12].upper()
            mapping.append({"review_id":opaque,"cohort":cohort,"url":url,
                            "source":lead["source"],"title":lead["title"]})
    rng=random.Random(SEED)
    rng.shuffle(mapping)
    if len({x["review_id"] for x in mapping})!=len(mapping):raise ValueError("Review ID collision")
    cards=[]
    for idx,entry in enumerate(mapping,1):
        raw=intake_map[entry["url"]]
        # Equal information budget. Capture metadata, not source's unbounded body.
        desc=" ".join(str(raw.get("description") or "").split())[:360]
        cards.append({"review_id":entry["review_id"],"sequence":idx,
                      "title":raw["title"][:180],"source_url":entry["url"],
                      "source_excerpt":desc or "NO_SOURCE_SUMMARY_PROVIDED",
                      "evidence_depth":"SOURCE_METADATA_ONLY",
                      "review_fields":{"ghostmesh_relevance":None,"novelty":None,
                                       "surprise":None,"best_objection":None,
                                       "source_review_required":None,"rationale":None}})
    packet={"schema":SCHEMA,"cards":cards,"case_count":len(cards),
       "review_instructions":{
         "time_budget_per_case_minutes":5,
         "max_additional_source_opens_per_case":1,
         "rule":"Assess all cases using the same rubric. Do not infer identities or use popularity as a score.",
         "scale":"0 no clear relevance; 1 speculative; 2 plausible concrete connection; 3 strong source-grounded connection",
         "novelty_scale":"0 familiar pattern; 1 possible variation; 2 materially different approach; ABSTAIN if evidence insufficient",
         "surprise_scale":"0 expected; 1 somewhat unexpected; 2 highly unexpected; ABSTAIN if evidence insufficient",
         "label_policy":"Only an independent reviewer may fill judgments; no automated positive or negative ground truth.",
         "missing_evidence":"ABSTAIN and record why; do not reward polished titles."},
       "limitations":["Labels and source cohort mapping are withheld from the reviewer packet",
                      "Source URLs, headlines and text may reveal an origin; cohort assignments and prior verdicts remain hidden",
                      "Equal metadata excerpts do not guarantee equal underlying source quality",
                      "This is a review-ready instrument, not an independent review outcome"],
       "publication_authorized":False,"outreach_authorized":False}
    sealed={"schema":"scout-blind-review-sealed-key-v0","review_ids":mapping,
            "unseal_only_after_review":True,"publication_authorized":False,"outreach_authorized":False}
    return packet,sealed

def evaluate(packet,key,ratings):
    if packet.get("schema")!=SCHEMA or key.get("schema")!="scout-blind-review-sealed-key-v0":
        raise ValueError("Unexpected review schema")
    if ratings.get("schema")!="scout-independent-review-labels-v0":raise ValueError("Missing independent ratings")
    expected={x["review_id"] for x in packet["cards"]}
    sealed={x["review_id"]:x for x in key["review_ids"]}
    if expected!=set(sealed):raise ValueError("Packet/key mismatch")
    provided=ratings.get("ratings",[])
    if len(provided)!=len(expected) or {x.get("review_id") for x in provided}!=expected:
        raise ValueError("Independent review must cover all 21 cases")
    usable=0;misses=0
    for x in provided:
        if x.get("ghostmesh_relevance") not in (0,1,2,3,"ABSTAIN"):
            raise ValueError("Invalid rating")
        if not isinstance(x.get("rationale"),str) or len(x["rationale"].strip())<12:
            raise ValueError("Missing independent reasoning")
        if x["ghostmesh_relevance"] in (2,3):
            usable+=1
            if sealed[x["review_id"]]["cohort"]=="OUTSIDE_BUBBLE":misses+=1
    return {"schema":"scout-independent-review-evaluation-v0",
        "rated":len(provided),"plausibly_relevant":usable,
        "relevant_outside_vocabulary":misses,
        "metric_name":"Outside-topic share of independently reviewed plausible connections",
        "not_a_recall_estimate":True,
        "limitations":["Purposeful source-balanced sampling, not a probability sample",
                       "One reviewer and heterogeneous evidence prevent population recall estimates",
                       "No claim of source originality or collaboration intent"],
        "publication_authorized":False,"outreach_authorized":False}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ("intake","triage","outside","packet","sealed"):ap.add_argument("--"+name,required=True,type=Path)
    a=ap.parse_args()
    if a.packet.exists() or a.sealed.exists():raise SystemExit("Refusing to overwrite review files")
    load=lambda x:json.loads(x.read_text(encoding="utf-8"))
    packet,sealed=make_packet(load(a.intake),load(a.triage),load(a.outside))
    a.packet.write_text(json.dumps(packet,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    a.sealed.write_text(json.dumps(sealed,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"blind_cards":packet["case_count"],"sealed_mapping":len(sealed["review_ids"])},indent=2))
if __name__=="__main__":main()
