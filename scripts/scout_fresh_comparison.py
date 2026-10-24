"""Prepare a new, fixed-budget Scout comparison from genuinely new source URLs.

Select six familiar-topic and eight outside-topic observations, with source
diversity. Retain the independent blind-review packet format and keep the
cohort key in a separate private file. Never call or label reviewers.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from scout_relevance_triage import triage

SEED="ghostmesh-fresh-scout-20261023-batch2"
def select(intake,previous,topic_quota=6,outside_quota=8):
    if intake.get("schema")!="scout-multisource-intake-v0" or previous.get("schema")!="scout-multisource-intake-v0":
        raise ValueError("Unexpected intake schema")
    if any(x.get("publication_authorized") is not False or x.get("outreach_authorized") is not False for x in (intake,previous)):
        raise ValueError("Owner-private research only")
    if type(topic_quota) is not int or type(outside_quota) is not int or not 1<=topic_quota<=12 or not 1<=outside_quota<=12:
        raise ValueError("Invalid bounded sample")
    old={x["url"] for x in previous["sampled_leads"]}
    current={x["url"]:x for x in intake["sampled_leads"]}
    if len(current)!=len(intake["sampled_leads"]):raise ValueError("Duplicate lead")
    current_triage=triage(intake)
    buckets={"TOPIC_MATCHED":defaultdict(list),"OUTSIDE_BUBBLE":defaultdict(list)}
    for result in current_triage["entries"]:
        url=result["url"]
        if url in old:continue
        item=current[url]
        cohort="TOPIC_MATCHED" if result["topics"] else "OUTSIDE_BUBBLE"
        buckets[cohort][item["source"]].append(item)
    rng=random.Random(SEED)
    chosen=[]
    for cohort,quota in (("TOPIC_MATCHED",topic_quota),("OUTSIDE_BUBBLE",outside_quota)):
        by_source=buckets[cohort]
        for entries in by_source.values():
            entries.sort(key=lambda x:hashlib.sha256((SEED+"|"+x["url"]).encode()).hexdigest())
        names=sorted(by_source)
        rng.shuffle(names)
        offset=0
        while len([x for x in chosen if x["cohort"]==cohort])<quota:
            progressed=False
            for name in names:
                if offset<len(by_source[name]):
                    chosen.append({"cohort":cohort,**by_source[name][offset]})
                    progressed=True
                    if len([x for x in chosen if x["cohort"]==cohort])==quota:break
            if not progressed:break
            offset+=1
        if len([x for x in chosen if x["cohort"]==cohort])!=quota:
            raise ValueError("Insufficient new observations for balanced review")
    # Avoid crowding the source distributions while leaving the snapshot intact.
    mapping=[]
    cards=[]
    for row in chosen:
        url=row["url"]
        review_id="SC2-"+hashlib.sha256((SEED+"|"+url).encode()).hexdigest()[:12].upper()
        mapping.append({"review_id":review_id,"cohort":row["cohort"],"url":url,
                        "source":row["source"],"title":row["title"]})
        cards.append({"review_id":review_id,"title":row["title"][:180],
                      "source_url":url,"source_excerpt":" ".join(str(row.get("description") or "").split())[:360] or "NO_SUMMARY",
                      "review_state":"NOT_REVIEWED","relevance":None,"novelty":None,"surprise":None})
    if len({x["review_id"] for x in cards})!=len(cards):raise ValueError("Review ID collision")
    rng.shuffle(cards)
    for i,card in enumerate(cards,1):card["sequence"]=i
    review={"schema":"scout-fresh-blind-review-v0","case_count":len(cards),"cards":cards,
        "review_budget":{"minutes_per_case":5,"additional_source_opens":1,
                         "required_fields":["relevance","novelty","surprise","strongest_objection","source_inspected","rationale"],
                         "relevance_scale":"0 none; 1 speculative; 2 concrete; 3 strong; ABSTAIN if inaccessible"},
        "source_coverage":{"captured_utc":intake.get("captured_utc"),"observed_total":len(current),
                           "new_urls":sum(x not in old for x in current),
                           "new_topic_count":sum(len(v) for v in buckets["TOPIC_MATCHED"].values()),
                           "new_outside_count":sum(len(v) for v in buckets["OUTSIDE_BUBBLE"].values())},
        "reviewer_note":"All cases are unreviewed. Source URL and title can reveal origins; topical cohort and prior editorial judgments are withheld.",
        "publication_authorized":False,"outreach_authorized":False}
    sealed={"schema":"scout-fresh-blind-key-v0","cohort_map":mapping,
            "unseal_only_after_all_ratings":True,"publication_authorized":False,"outreach_authorized":False}
    return review,sealed

def main():
    p=argparse.ArgumentParser()
    for name in ("intake","previous","packet","sealed"):p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    if a.packet.exists() or a.sealed.exists():raise SystemExit("Refusing overwrite")
    load=lambda path:json.loads(path.read_text(encoding="utf-8"))
    packet,key=select(load(a.intake),load(a.previous))
    a.packet.write_text(json.dumps(packet,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    a.sealed.write_text(json.dumps(key,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"review_cases":packet["case_count"],"new_urls":packet["source_coverage"]["new_urls"],
       "sources":len({x["source"] for x in key["cohort_map"]})}))
if __name__=="__main__":main()
