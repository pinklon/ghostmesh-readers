"""Run-bound owner-private builder/account observations and connection questions.

No person verification or automatic assessment. Links only current intake work.
"""
from __future__ import annotations
from html import escape
from urllib.parse import urlsplit
import hashlib

def build(intake,triage):
    if intake.get("schema")!="scout-multisource-intake-v0" or triage.get("schema")!="scout-relevance-triage-v0":
        raise ValueError("Invalid input")
    if any(x.get("publication_authorized") is not False or x.get("outreach_authorized") is not False for x in (intake,triage)):
        raise ValueError("Private only")
    by={x["url"]:x for x in triage["entries"]}
    if len(by)!=len(triage["entries"]) or set(by)!={x["url"] for x in intake["sampled_leads"]}:
        raise ValueError("Incomplete triage")
    people=[];questions=[]
    for lead in intake["sampled_leads"]:
        row=by[lead["url"]]
        identity=row.get("identity")
        if identity:
            name=str(identity.get("value") or "").strip()
            if not name or identity.get("verified_person") is not False:
                raise ValueError("Untrusted identity")
            people.append({"id":hashlib.sha256(lead["url"].encode()).hexdigest()[:14],
                "label":name,"kind":identity["type"],"url":lead["url"],"title":lead["title"],
                "identity_verified":False,"contact_authorized":False})
        if row.get("topics"):
            questions.append({"url":lead["url"],"title":lead["title"],
                "topics":row["topics"],"ghostmesh_questions":row.get("ghostmesh_questions",[]),
                "disposition":"UNASSESSED","source_verified":False,"counterargument":"NOT_REVIEWED",
                "outreach_authorized":False})
    return {"schema":"scout-run-builder-questions-v0","people":people,"questions":questions,
        "people_are":"Observed feed or repository account labels, not independently verified people",
        "questions_are":"Keyword-generated research questions, not defended connection theses",
        "publication_authorized":False,"outreach_authorized":False}

def render(data,kind):
    if data.get("schema")!="scout-run-builder-questions-v0" or kind not in ("people","questions") or data.get("publication_authorized") is not False or data.get("outreach_authorized") is not False:
        raise ValueError("Invalid private view")
    e=lambda x:escape(str(x or ""),quote=True)
    title="Observed builder accounts" if kind=="people" else "Connections to investigate"
    intro=data["people_are"] if kind=="people" else data["questions_are"]
    body=[]
    for row in data[kind]:
        if row.get("outreach_authorized") is not False and kind=="questions":raise ValueError("Outreach forbidden")
        url=urlsplit(row["url"])
        if url.scheme!="https" or not url.hostname or url.username or url.password:raise ValueError("Invalid source")
        heading=row["label"] if kind=="people" else row["title"]
        body.extend(["<article><small>",e(row.get("kind","QUESTION NOT VERIFIED")),"</small><h2>",e(heading),"</h2><p><a href='",e(row["url"] ),"' target='_blank' rel='noopener noreferrer'>Inspect original public work ↗</a></p>"])
        if kind=="people":
            body.extend(["<p>Observed through: ",e(row["title"]),"</p><p>Identity verified: NO · Outreach authorized: NO</p>"])
        else:
            body.extend(["<p>Topics: ",e(", ".join(row["topics"])),"</p><p>Questions: ",e("; ".join(row["ghostmesh_questions"])),"</p><p>Originality, counterevidence and technical transfer: NOT REVIEWED.</p>"])
        body.append("</article>")
    return "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow,noarchive'><title>Scout / Current run</title><style>:root{color-scheme:dark}body{margin:0;background:#111318;color:#f2f3f5;font:15px/1.6 system-ui}header,main,footer{max-width:1120px;margin:auto;padding:28px}h1{font-size:clamp(34px,6vw,64px);letter-spacing:-.05em;line-height:1.08}article{padding:22px 0;border-top:1px solid #454952}p{color:#c2c5cc}a{color:#ffb1be}small{color:#fa647b}</style></head><body><header><small>GHOSTMESH SCOUT · UNVERIFIED CURRENT-RUN EVIDENCE</small><h1>"+e(title)+"</h1><p>"+e(intro)+"</p><p>"+str(len(data[kind]))+" records. No implied identity resolution or collaboration.</p></header><main>"+"".join(body)+"</main><footer>Private metadata observations · No inferred verified claims or outreach</footer></body></html>"
