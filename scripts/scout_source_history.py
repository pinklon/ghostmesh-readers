"""Build source and relationship histories from successive sampled Scout snapshots.

Disappearance from a sample is not deletion. No inferred momentum or outreach.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def build(history: list[tuple[dict, dict]]) -> dict:
    if len(history) < 2:
        raise ValueError("At least two observation snapshots required")
    records={}
    timestamps=[]
    for index,(intake,triage) in enumerate(history):
        if intake.get("schema") != "scout-multisource-intake-v0" or triage.get("schema") != "scout-relevance-triage-v0":
            raise ValueError("Unexpected schema")
        if any(x.get("publication_authorized") is not False or x.get("outreach_authorized") is not False for x in (intake,triage)):
            raise ValueError("Research-only inputs required")
        captured=intake.get("captured_utc")
        if not isinstance(captured,str) or not captured:
            raise ValueError("Collection timestamp missing")
        if timestamps and captured <= timestamps[-1]:
            raise ValueError("Snapshots must be strictly chronological")
        timestamps.append(captured)
        details={x["url"]:x for x in triage["entries"]}
        observed=set()
        for lead in intake["sampled_leads"]:
            url=lead["url"]
            if url in observed: continue
            observed.add(url)
            if url not in details: raise ValueError("Triage does not cover source")
            d=details[url]
            topics=sorted(set(d.get("topics",[])))
            identity=d.get("identity")
            handle=(identity["type"]+":"+identity["value"].lower()) if identity else None
            item=records.setdefault(url,{"id":"source:"+hashlib.sha256(url.encode()).hexdigest()[:16],
                "url":url,"title":lead["title"],"first_seen":captured,
                "last_seen":captured,"observation_count":0,"observations":[]})
            item["last_seen"]=captured
            item["observation_count"]+=1
            item["observations"].append({"snapshot_index":index,"captured_utc":captured,
                "title":lead["title"],"topics":topics,"observed_handle":handle})
    entries=[]
    for url,item in sorted(records.items()):
        obs=item["observations"]
        changes=[]
        for before,after in zip(obs,obs[1:]):
            added=sorted(set(after["topics"])-set(before["topics"]))
            removed=sorted(set(before["topics"])-set(after["topics"]))
            if added or removed:
                changes.append({"type":"METADATA_TOPIC_DELTA","captured_utc":after["captured_utc"],
                    "added":added,"removed":removed,"certainty":"HEURISTIC"})
            if after["title"] != before["title"]:
                changes.append({"type":"TITLE_METADATA_DELTA","captured_utc":after["captured_utc"],
                    "certainty":"OBSERVED_METADATA"})
            if after["observed_handle"] != before["observed_handle"]:
                changes.append({"type":"HANDLE_METADATA_DELTA","captured_utc":after["captured_utc"],
                    "certainty":"OBSERVED_METADATA_NOT_PERSON_IDENTITY"})
        if obs[-1]["snapshot_index"] != len(history)-1:
            changes.append({"type":"ABSENT_FROM_LATEST_SAMPLE","captured_utc":timestamps[-1],
                "certainty":"SAMPLING_ONLY"})
        item["changes"]=changes
        item["current_sample_state"]="PRESENT" if obs[-1]["snapshot_index"]==len(history)-1 else "NOT_IN_LATEST_SAMPLE"
        entries.append(item)
    return {"schema":"scout-source-history-v0","snapshots":timestamps,"sources":entries,
            "counts":{"distinct_sources":len(entries),
                      "seen_in_multiple_snapshots":sum(x["observation_count"]>1 for x in entries),
                      "not_in_latest_sample":sum(x["current_sample_state"]!="PRESENT" for x in entries),
                      "metadata_events":sum(len(x["changes"]) for x in entries)},
            "limitations":["Feed membership is not evidence of creation, deletion or growth",
                          "Topic changes reflect metadata vocabulary, not confirmed changes in an idea",
                          "Observed handles do not establish human identity or social relationship",
                          "No claim-level revision history until individually verified primary sources are retained"],
            "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot",action="append",nargs=2,metavar=("INTAKE","TRIAGE"),required=True)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Output already exists")
    pair=[(json.loads(Path(i).read_text(encoding="utf-8")),
           json.loads(Path(t).read_text(encoding="utf-8"))) for i,t in a.snapshot]
    result=build(pair)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result["counts"],indent=2))
if __name__=="__main__": main()
