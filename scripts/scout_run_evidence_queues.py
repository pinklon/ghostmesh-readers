"""Current-run evidence queues. Source metadata is not verified claim content."""
from __future__ import annotations
import json
from html import escape
from urllib.parse import urlsplit

def build(intake, triage):
    if intake.get("schema") != "scout-multisource-intake-v0" or triage.get("schema") != "scout-relevance-triage-v0":
        raise ValueError("Invalid Scout inputs")
    if any(x.get("publication_authorized") is not False or x.get("outreach_authorized") is not False for x in (intake,triage)):
        raise ValueError("Research only")
    lookup={x["url"]:x for x in triage["entries"]}
    if len(lookup)!=len(triage["entries"]) or set(lookup)!={x["url"] for x in intake["sampled_leads"]}:
        raise ValueError("Unreconciled triage")
    works=[]
    for x in intake["sampled_leads"]:
        url=x["url"];p=urlsplit(url)
        if p.scheme!="https" or not p.hostname or p.username or p.password:
            raise ValueError("Invalid link")
        works.append({"url":url,"title":x["title"],"source":x["source"],
                      "excerpt":str(x.get("description") or "")[:500],
                      "topics":lookup[url].get("topics",[]),"verified":False})
    return {"schema":"scout-run-evidence-queues-v0",
            "works":works,"claims":[x for x in works if x["topics"]],
            "publication_authorized":False,"outreach_authorized":False}

def render(data,kind):
    if data.get("schema")!="scout-run-evidence-queues-v0" or kind not in ("works","claims"):
        raise ValueError("Invalid view")
    if data.get("publication_authorized") is not False or data.get("outreach_authorized") is not False:
        raise ValueError("Private view only")
    esc=lambda x:escape(str(x or ""),quote=True)
    intro=("Candidate feed excerpts requiring primary-source review; no revision is pinned or factual claim verified."
           if kind=="claims" else "Original source URLs observed in this run, not expanded same-person contribution trails.")
    parts=["<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow,noarchive'><title>Scout / Evidence</title><style>:root{color-scheme:dark}body{margin:0;background:#111318;color:#f5f5f6;font:15px/1.6 system-ui,sans-serif}main,header,footer{max-width:1100px;margin:auto;padding:30px}h1{font-size:clamp(34px,6vw,60px);line-height:1.05}article{padding:20px 0;border-top:1px solid #555}a{color:#ffb3c0}p{color:#bdc1c9}</style></head><body><header><h1>",esc("Claims needing evidence" if kind=="claims" else "Public work observed"),"</h1><p>",esc(intro),"</p><p>",str(len(data[kind]))," unverified leads</p></header><main>"]
    for item in data[kind]:
        parts.extend(["<article><small>",esc(item["source"]),"</small><h2><a rel='noopener noreferrer' target='_blank' href='",esc(item["url"]),"'>",esc(item["title"]),"</a></h2><p>Topics: ",esc(", ".join(item["topics"]) or "Unmatched"),"</p>"])
        if kind=="claims":
            parts.extend(["<p>Unverified feed summary: ",esc(item["excerpt"] or "Unavailable"),"</p><p>Primary-source examination and source-revision witness: NOT DONE.</p>"])
        parts.append("</article>")
    parts.append("</main><footer>Owner-private research. No source claim validated, identity inferred, or outreach authorized.</footer></body></html>")
    return "".join(parts)
