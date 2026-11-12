"""Current-run Scout decision receipts and capability *questions*.

Read-only metadata audit. No agent execution replay or measured GhostMesh delta.
"""
from __future__ import annotations
from html import escape
from collections import Counter

def build(intake, triage, edition, reconcile):
    expected=("scout-multisource-intake-v0","scout-relevance-triage-v0",
              "scout-private-edition-v0","scout-reconciliation-v0")
    if tuple(x.get("schema") for x in (intake,triage,edition,reconcile))!=expected:
        raise ValueError("Unsupported run schema")
    if any(x.get("publication_authorized") is not False or x.get("outreach_authorized") is not False
           for x in (intake,triage,edition,reconcile)):
        raise ValueError("Research-only inputs")
    entries={x["url"]:x for x in triage["entries"]}
    sources={x["url"]:x for x in intake["sampled_leads"]}
    if len(sources)!=len(intake["sampled_leads"]) or set(entries)!=set(sources):
        raise ValueError("Run/triage coverage mismatch")
    selected={x["url"]:x for x in edition["candidates"]}
    if not set(selected).issubset(sources):raise ValueError("Unknown selected source")
    receipts=[]
    for url, lead in sources.items():
        t=entries[url]
        chosen=selected.get(url)
        receipts.append({
           "url":url,"title":lead["title"],"source":lead["source"],
           "topics":list(t.get("topics",[])),
           "heuristic_status":t["relevance_status"],
           "queue":"NOT_SELECTED" if chosen is None else chosen["queue"],
           "decision_basis":"DECLARED_KEYWORD_MATCH_AND_WATCH_CATALOG",
           "primary_source_verified":False,"model_inference_used":False,
           "outreach_authorized":False})
    by_topic=Counter(tag for x in entries.values() for tag in x["topics"])
    questions=[{"topic":topic,"observed_leads":count,
                "known_ghostmesh_capability":"NOT_MEASURED",
                "capability_improvement":"NOT_MEASURED",
                "question":"Is this approach already implemented, useful, or contradicted by GhostMesh evidence?",
                "source_evidence":"SOURCE_METADATA_ONLY","outreach_authorized":False}
               for topic,count in sorted(by_topic.items())]
    return {"schema":"scout-current-run-audit-v0",
            "receipts":receipts,"capability_questions":questions,
            "total":len(receipts),"selected":len(selected),
            "limits":["Reconstructs deterministic intake/triage selections, NOT real agent execution",
                      "Topic observations are NOT measured capability improvements",
                      "No source content verification or author identity matching"],
            "publication_authorized":False,"outreach_authorized":False}

def render(audit, kind):
    if audit.get("schema")!="scout-current-run-audit-v0" or kind not in ("replay","differences"):
        raise ValueError("Invalid audit")
    if audit.get("publication_authorized") is not False or audit.get("outreach_authorized") is not False:
        raise ValueError("Private only")
    e=lambda x:escape(str(x or ""),quote=True)
    rows=audit["receipts"] if kind=="replay" else audit["capability_questions"]
    title="Why Scout surfaced each signal" if kind=="replay" else "Capability questions, not measured deltas"
    caution=("This is a reconstruction of deterministic keyword and catalog decisions, not an execution trace of autonomous agents."
       if kind=="replay" else "No GhostMesh implementation was inspected or benchmarked; improvement and capability status remain NOT MEASURED.")
    parts=["<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow,noarchive'><title>Scout / Current-run audit</title><style>:root{color-scheme:dark}body{margin:0;background:#111318;color:#f4f4f5;font:15px/1.6 system-ui,sans-serif}header,main,footer{max-width:1120px;margin:auto;padding:28px}h1{font-size:clamp(35px,6vw,63px);letter-spacing:-.05em;line-height:1.08}article{border-top:1px solid #464950;padding:19px 0}p,footer{color:#c4c8d0}a{color:#ffb2bd}small{color:#f16a7e}</style></head><body><header><small>GHOSTMESH / SCOUT · SOURCE-BOUND RESEARCH</small><h1>",e(title),"</h1><p>",e(caution),"</p><p>",str(len(rows))," records</p></header><main>"]
    for x in rows:
        if kind=="replay":
            parts.extend(["<article><small>",e(x["queue"]),"</small><h2><a href='",e(x["url"]),"' target='_blank' rel='noopener noreferrer'>",e(x["title"]),"</a></h2><p>Source: ",e(x["source"])," · Topics: ",e(", ".join(x["topics"]) or "none"),"</p><p>Method: keyword/watch catalog; no model inference or verification.</p></article>"])
        else:
            parts.extend(["<article><h2>",e(x["topic"].replace("-"," ").title()),"</h2><p>",str(x["observed_leads"])," metadata topic matches. GhostMesh baseline: NOT MEASURED. Improvement: NOT MEASURED.</p><p>",e(x["question"]),"</p></article>"])
    parts.append("</main><footer>No deployment, automatic research endorsement, author contact, or permission granted.</footer></body></html>")
    return "".join(parts)
