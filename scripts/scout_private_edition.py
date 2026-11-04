"""Create a compact private Scout edition with source-linked, non-authoritative watch signals."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from html import escape

def edition(intake, triage, catalog):
    if intake.get("schema")!="scout-multisource-intake-v0" or triage.get("schema")!="scout-relevance-triage-v0" or catalog.get("schema")!="scout-watch-catalog-v0":
        raise ValueError("Unexpected schema")
    if catalog.get("publication_authorized") is not False or catalog.get("outreach_authorized") is not False:
        raise ValueError("Invalid permissions")
    lookup={x["url"]:x for x in triage["entries"]}
    items=[]
    for lead in intake["sampled_leads"]:
        url=lead["url"]
        if url not in lookup:continue
        relevance=lookup[url]
        text=(lead.get("title","")+" "+lead.get("description","")).lower()
        host=urlsplit(url).hostname or ""
        matches=[]
        for watch in catalog["watches"]:
            keys=watch.get("keywords",[])
            verified_host=watch.get("source_host")
            if verified_host and (host==verified_host or host.endswith("."+verified_host)):
                matches.append({"watch":watch["id"],"reason":"source-host-match"})
            elif any(key.lower() in text for key in keys):
                matches.append({"watch":watch["id"],"reason":"metadata-keyword-match"})
        if not matches and not relevance["topics"]:continue
        items.append({"url":url,"title":lead["title"],"source":lead["source"],
                      "lane":lead["lane"],"topics":relevance["topics"],
                      "watches":matches,"match_status":"UNVERIFIED_METADATA_MATCH",
                      "ghostmesh_questions":relevance["ghostmesh_questions"],
                      "editorial_judgment":"NOT_ASSESSED",
                      "queue":"FOCUS_REVIEW" if relevance["topics"] else "BACKGROUND_WATCH",
                      "outreach_authorized":False})
    # Curated watches receive attention but are not an approval or significance rank.
    items.sort(key=lambda x:(x["queue"] != "FOCUS_REVIEW",not bool(x["watches"]),-len(x["topics"]),x["source"],x["title"]))
    return {"schema":"scout-private-edition-v0","captured_utc":intake.get("captured_utc"),
            "total_sampled":len(intake["sampled_leads"]),"candidate_count":len(items),
            "focus_count":sum(x["queue"]=="FOCUS_REVIEW" for x in items),
            "candidates":items,
            "source_health":intake.get("diagnostics",[]),
            "limits":["This is a filtered reading queue, not verified intelligence or measured trends",
                      "Named-person matching by words does not establish authorship or identity",
                      "External social accounts and private collaboration messages are not ingested",
                      "Source metadata is not independently checked against full article content"],
            "publication_authorized":False,"outreach_authorized":False}

def markdown(result, max_cases=18):
    lines=["# GhostMesh Scout | Private discovery edition","",
           "This is an unreviewed reading queue. No ranking of truth, novelty, virality, or collaborator readiness.","",
           f"Observed {result['total_sampled']} public leads; {result['candidate_count']} matched a curated watch or topic heuristic.",""]
    for item in result["candidates"][:max_cases]:
        lines += [f"## {item['title']}","",f"Source: {item['url']}",
                  f"Stream: {item['source']} / {item['lane']}",
                  f"Queue: {item['queue']}",
                  "Watch matches: "+(", ".join(w["watch"]+" ("+w["reason"]+")" for w in item["watches"]) or "none"),
                  "Possible GhostMesh connections: "+("; ".join(item["ghostmesh_questions"]) or "not established"),
                  "Status: UNVERIFIED_METADATA_MATCH. Editorial review required.",""]
    lines += ["## Method and caveats",""]+["- "+x for x in result["limits"]]
    return "\n".join(lines)+"\n"

def main():
    p=argparse.ArgumentParser()
    for key in ("intake","triage","watches","out"):p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing to overwrite edition")
    load=lambda p:json.loads(p.read_text(encoding="utf-8"))
    result=edition(load(a.intake),load(a.triage),load(a.watches))
    a.out.write_text(markdown(result),encoding="utf-8")
    print(json.dumps({"total_sampled":result["total_sampled"],"candidate_count":result["candidate_count"],"output":str(a.out)}))
if __name__=="__main__":main()
