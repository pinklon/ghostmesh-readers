"""Scout lead reconciliation v0: stable URLs, cross-source coverage, and temporal deltas.

One observation is not a trend. No autonomous promotion, publication, or outreach.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING = {"fbclid", "gclid", "igshid", "mc_cid", "mc_eid", "ref_src"}
def canonical_url(url: str) -> str:
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        raise ValueError("Expected safe HTTPS URL")
    host = p.hostname.lower()
    query = [(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in TRACKING]
    path = p.path.rstrip("/") or "/"
    if host in {"www.github.com", "github.com"}:
        host = "github.com"
    if host in {"www.youtube.com", "m.youtube.com", "youtube.com"}:
        host = "www.youtube.com"
        values = dict(query)
        if path in {"/watch", "/shorts"} and (values.get("v") or path=="/shorts"):
            vid = values.get("v") if path=="/watch" else path.split("/")[-1]
            if vid:
                path="/watch"
                query=[("v",vid)]
    if host == "youtu.be":
        vid = path.strip("/")
        if vid:
            host="www.youtube.com";path="/watch";query=[("v",vid)]
    return urlunsplit(("https",host,path,urlencode(sorted(query)),""))

def reconcile(current: dict, previous: dict | None = None) -> dict:
    if current.get("schema") != "scout-multisource-intake-v0":
        raise ValueError("Invalid current snapshot schema")
    if previous is not None and previous.get("schema") != "scout-multisource-intake-v0":
        raise ValueError("Invalid prior snapshot schema")
    def group(data):
        grouped={}
        for lead in data.get("sampled_leads", []):
            if lead.get("status") != "UNREVIEWED_LEAD":
                raise ValueError("Cannot reconcile promoted or altered leads")
            canonical=canonical_url(lead["url"])
            grouped.setdefault(canonical,[]).append(lead)
        return grouped
    curr,prev=group(current),group(previous) if previous else {}
    unique=[]
    for url, observations in sorted(curr.items()):
        sources=sorted(set(o["source"] for o in observations))
        lanes=sorted(set(o["lane"] for o in observations))
        before=prev.get(url,[])
        changed_text=bool(before and (
            {(x.get("title",""),x.get("description","")) for x in observations} !=
            {(x.get("title",""),x.get("description","")) for x in before}))
        unique.append({"url":url,"title":observations[0]["title"],
            "sources":sources,"lanes":lanes,"observations":len(observations),
            "state":"NEW_TO_SAMPLE" if not before else "METADATA_CHANGED" if changed_text else "SEEN_AGAIN",
            "cross_source":len(sources)>1,
            "assessment":"UNREVIEWED","trend":"NOT_MEASURED","relevance":"UNKNOWN",
            "outreach_authorized":False})
    gone=sorted(set(prev)-set(curr))
    # A source disappearing from a top-N snapshot does not mean it was removed from the internet.
    return {"schema":"scout-reconciliation-v0",
        "current_captured_utc":current.get("captured_utc"),
        "previous_captured_utc":previous.get("captured_utc") if previous else None,
        "raw_leads":len(current.get("sampled_leads",[])),
        "canonical_leads":len(unique),
        "cross_source_count":sum(x["cross_source"] for x in unique),
        "new_to_sample":sum(x["state"]=="NEW_TO_SAMPLE" for x in unique),
        "metadata_changed":sum(x["state"]=="METADATA_CHANGED" for x in unique),
        "missing_from_current_sample":len(gone),
        "absent_sample_urls":gone[:30],
        "leads":unique,
        "limits":["Only compared sampled top-N retrievals; missing is not deleted",
                  "Metadata changes are not evidence of substantive changes",
                  "No measured velocity, virality, importance, or verified content",
                  "Same-topic different-URL items are not automatically merged"],
        "publication_authorized":False,"outreach_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--current",required=True,type=Path)
    p.add_argument("--previous",type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    current=json.loads(a.current.read_text(encoding="utf-8"))
    previous=json.loads(a.previous.read_text(encoding="utf-8")) if a.previous else None
    result=reconcile(current,previous)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k in ("raw_leads","canonical_leads","cross_source_count","new_to_sample","metadata_changed","missing_from_current_sample")},indent=2))

if __name__=="__main__":main()
