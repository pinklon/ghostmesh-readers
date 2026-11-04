"""Conservative work-to-capability triage for public Scout trails.

Finds vocabulary-supported investigation questions against a declared GhostMesh
baseline. Never claims work is original, missing locally, or a collaborator fit.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

def assess(trails:dict,baseline:dict)->dict:
    if trails.get("schema")!="scout-public-contribution-trails-v0" or baseline.get("schema")!="scout-existing-capabilities-v0":
        raise ValueError("Unexpected research schema")
    for obj in (trails,baseline):
        if obj.get("publication_authorized") is not False or obj.get("outreach_authorized") is not False:
            raise ValueError("Research only")
    if trails.get("identity_verified") is not False:raise ValueError("Identity not established")
    capabilities=baseline.get("capabilities",[])
    if not capabilities or len({x["id"] for x in capabilities})!=len(capabilities):raise ValueError("Invalid baseline")
    for cap in capabilities:
        if not all(cap.get(k) for k in ("id","label","current","evidence","keywords","question","known_gap","anti_claim")):
            raise ValueError("Incomplete local baseline")
    rows=[];seen=set()
    for item in trails.get("trails",[]):
        if item.get("contact_authorized") is not False or item.get("same_real_person_confirmed") is not False:
            raise ValueError("Unverified contributor trail")
        if item.get("id") in seen:raise ValueError("Duplicate work attribution ID")
        seen.add(item["id"])
        u=urlsplit(item.get("work_url",""))
        if u.scheme!="https" or u.username or u.password or u.hostname not in ("github.com","arxiv.org"):
            raise ValueError("Only public-source URLs")
        text=" ".join(str(item.get(k) or "") for k in ("work_title","description")).casefold()
        candidates=[]
        for cap in capabilities:
            tokens=[phrase for phrase in cap["keywords"] if phrase.casefold() in text]
            if not tokens:continue
            candidates.append({"capability_id":cap["id"],"capability":cap["label"],
               "matched_metadata_terms":tokens,
               "existing_ghostmesh_baseline":cap["current"],
               "baseline_evidence":cap["evidence"],
               "possible_gap_to_test":cap["known_gap"],
               "discriminating_question":cap["question"],
               "strongest_objection":cap["anti_claim"],
               "source_review":"REQUIRED",
               "capability_absent":"NOT_ESTABLISHED",
               "originality":"NOT_ASSESSED",
               "incremental_value":"NOT_MEASURED"})
        rows.append({"id":item["id"],"attribution":item["label"],
            "trail_kind":item["kind"],"work_title":item.get("work_title",""),
            "work_url":item["work_url"],"origin_work":item.get("origin_work",""),
            "identity_verified":False,"status":"REVIEW_POTENTIAL_DELTA" if candidates else "NO_METADATA_EVIDENCE",
            "candidates":candidates,"outreach_authorized":False})
    return {"schema":"scout-capability-delta-triage-v0",
        "total_trails":len(rows),
        "trails_with_potential_delta":sum(bool(x["candidates"]) for x in rows),
        "potential_delta_links":sum(len(x["candidates"]) for x in rows),
        "rows":rows,
        "limitations":["Keyword occurrences in titles/descriptions only; no automatic source validation",
                       "A gap in measurement is not proof a GhostMesh capability is missing",
                       "One work can match multiple categories; counts are not unique people or independent findings",
                       "No popularity scoring, collaborator qualification, code execution or outreach"],
        "baseline_status":baseline.get("status"),
        "publication_authorized":False,"outreach_authorized":False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for k in ("trails","baseline","out"):parser.add_argument("--"+k,required=True,type=Path)
    a=parser.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    read=lambda p:json.loads(p.read_text(encoding="utf-8"))
    r=assess(read(a.trails),read(a.baseline))
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:r[k] for k in ("total_trails","trails_with_potential_delta","potential_delta_links")},indent=2))
if __name__=="__main__":main()
