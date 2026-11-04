"""Build cautious relations from Scout's observed public-source metadata."""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

def build(intake: dict, triage: dict, history: dict) -> dict:
    expected = ("scout-multisource-intake-v0","scout-relevance-triage-v0","scout-reconciliation-v0")
    if tuple(x.get("schema") for x in (intake,triage,history)) != expected:
        raise ValueError("Unknown input schema")
    if any(x.get("publication_authorized") is not False or x.get("outreach_authorized") is not False
           for x in (intake,triage,history)):
        raise ValueError("Research-only authority required")
    assessments = {x["url"]: x for x in triage["entries"]}
    states = {x["url"]: x["state"] for x in history["leads"]}
    nodes,edges=[],[]
    topic_groups=defaultdict(list)
    handle_groups=defaultdict(list)
    seen=set()
    for lead in intake["sampled_leads"]:
        url=lead["url"]
        if url in seen: continue
        seen.add(url)
        if url not in assessments: raise ValueError("Missing source triage")
        sid="source:"+hashlib.sha256(url.encode()).hexdigest()[:16]
        nodes.append({"id":sid,"kind":"source","url":url,"title":lead["title"],
                      "sample_state":states.get(url,"UNKNOWN"),"verified_content":False})
        item=assessments[url]
        for topic in item.get("topics",[]):topic_groups[topic].append(sid)
        identity=item.get("identity")
        if identity:
            handle_groups[identity["type"]+":"+identity["value"].lower()].append(sid)
    for topic,ids in sorted(topic_groups.items()):
        tid="topic:"+topic
        nodes.append({"id":tid,"kind":"topic","label":topic})
        edges.extend({"from":sid,"to":tid,"relation":"METADATA_TOPIC_MATCH",
                      "confidence":"HEURISTIC"} for sid in sorted(set(ids)))
    for handle,ids in sorted(handle_groups.items()):
        hid="handle:"+handle
        nodes.append({"id":hid,"kind":"observed_handle","label":handle,"person_verified":False})
        edges.extend({"from":sid,"to":hid,"relation":"OBSERVED_SOURCE_HANDLE",
                      "confidence":"METADATA_ONLY"} for sid in sorted(set(ids)))
    return {"schema":"scout-relations-v0","nodes":nodes,"edges":edges,
            "counts":{"sources":len(seen),"topic_links":sum(x["relation"]=="METADATA_TOPIC_MATCH" for x in edges),
                      "handle_links":sum(x["relation"]=="OBSERVED_SOURCE_HANDLE" for x in edges)},
            "limits":["Shared vocabulary does not establish common authorship or the same event",
                      "Source handles do not establish real-world personal identity",
                      "No collaborator, referral or endorsement relation is inferred"],
            "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser()
    for arg in ("intake","triage","history","out"):p.add_argument("--"+arg,required=True,type=Path)
    args=p.parse_args()
    if args.out.exists():raise SystemExit("Output exists")
    read=lambda path:json.loads(path.read_text(encoding="utf-8"))
    result=build(read(args.intake),read(args.triage),read(args.history))
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result["counts"]))
if __name__=="__main__":main()
