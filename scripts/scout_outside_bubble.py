"""Select a visible outside-the-bubble exploration cohort from Scout's existing intake.

Deterministic source-balanced sampling of *unmatched* leads. No relevance,
novelty, identity, or human-benefit labels are fabricated. Shadow filtering
only reports what a topic-only view would hide; it never discards records.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA="scout-outside-bubble-v0"
def build(intake,triage,*,per_source=2,max_total=12):
    if intake.get("schema")!="scout-multisource-intake-v0" or triage.get("schema")!="scout-relevance-triage-v0":
        raise ValueError("Unexpected source schema")
    for obj in (intake,triage):
        if obj.get("publication_authorized") is not False or obj.get("outreach_authorized") is not False:
            raise ValueError("Private research required")
    if type(per_source) is not int or type(max_total) is not int or not 1<=per_source<=5 or not 1<=max_total<=30:
        raise ValueError("Invalid bounded exploration quotas")
    entries=triage.get("entries",[])
    lookup={}
    for t in entries:
        url=t.get("url")
        if url in lookup:raise ValueError("Duplicate triage URL")
        lookup[url]=t
    sampled=intake.get("sampled_leads",[])
    if len({x["url"] for x in sampled})!=len(sampled) or set(lookup)!={x["url"] for x in sampled}:
        raise ValueError("Triage must cover intake exactly")
    outside=defaultdict(list)
    topical=0;all_rows=[]
    for item in sampled:
        t=lookup[item["url"]]
        unmatched=not bool(t.get("topics"))
        if not unmatched:topical+=1
        row={"url":item["url"],"title":item.get("title",""),"source":item["source"],
             "lane":item["lane"],"topics":t.get("topics",[]),
             "existing_topic_filter_would_hide":unmatched,
             "source_reviewed":False,"novelty":"UNASSESSED","relevance":"UNASSESSED",
             "human_review_result":"NOT_REVIEWED","outreach_authorized":False}
        all_rows.append(row)
        if unmatched:outside[item["source"]].append(row)
    # Stable within-source ordering is hash-based, not a popularity signal.
    for source in outside:
        outside[source].sort(key=lambda x:hashlib.sha256(x["url"].encode()).hexdigest())
    selected=[];used=Counter()
    # Round-robin creates source diversity without weighting stars/likes/views.
    while len(selected)<max_total:
        advanced=False
        for source in sorted(outside):
            if used[source]>=per_source or used[source]>=len(outside[source]):continue
            selected.append(dict(outside[source][used[source]],cohort="OUTSIDE_BUBBLE_SHADOW"))
            used[source]+=1;advanced=True
            if len(selected)==max_total:break
        if not advanced:break
    shadow_hidden=[x for x in all_rows if x["existing_topic_filter_would_hide"]]
    return {"schema":SCHEMA,"total":len(all_rows),"topic_matched":topical,
       "outside_topic_vocabulary":len(shadow_hidden),
       "outside_sampled":len(selected),"source_diversity":len({x["source"] for x in selected}),
       "outside_sample":selected,"shadow_hidden":shadow_hidden,
       "selection":"Deterministic SHA256 URL order within each source, then source round-robin; not a relevance score",
       "interpretation":"No human truth labels. Potential missed discoveries cannot be quantified until reviewed.",
       "limits":["Outside topic vocabulary means only unmatched against declared Scout terms",
                 "No relevance or originality ranking and no claim these are independent builders",
                 "Do not remove any source; original intake remains intact",
                 "Human review needed before measuring false negatives or surprise"],
       "publication_authorized":False,"outreach_authorized":False}
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ("intake","triage","out"):ap.add_argument("--"+k,type=Path,required=True)
    ap.add_argument("--per-source",type=int,default=2)
    ap.add_argument("--max-total",type=int,default=12)
    a=ap.parse_args()
    if a.out.exists():raise SystemExit("Refusing to overwrite")
    load=lambda p:json.loads(p.read_text(encoding="utf-8"))
    data=build(load(a.intake),load(a.triage),per_source=a.per_source,max_total=a.max_total)
    a.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:data[k] for k in ("total","topic_matched","outside_topic_vocabulary","outside_sampled","source_diversity")},indent=2))
if __name__=="__main__":main()
