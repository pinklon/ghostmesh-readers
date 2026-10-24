"""Contrast source-balanced outside discoveries with familiar topic matches.

Human ground truth remains absent. Editorial source reviews are optional,
separate from initial metadata sampling and NEVER used to change historical
triage labels or to infer unique collaborator identities.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from html import escape

def compare(outside,triage,editorial):
    if outside.get("schema")!="scout-outside-bubble-v0" or triage.get("schema")!="scout-relevance-triage-v0" or editorial.get("schema")!="scout-editorial-contrast-v0":
        raise ValueError("Unexpected evidence schema")
    for x in (outside,triage,editorial):
        if x.get("publication_authorized") is not False or x.get("outreach_authorized") is not False:raise ValueError("Private review only")
    sampled={x["url"]:x for x in outside["outside_sample"]}
    familiar={x["url"]:x for x in triage["entries"] if x.get("topics")}
    reviews={}
    for a in editorial["assessments"]:
        url=a["url"]
        if url in reviews:raise ValueError("Duplicate assessment")
        expected="OUTSIDE_BUBBLE" if url in sampled else "TOPIC_MATCHED" if url in familiar else None
        if expected is None or a["cohort"]!=expected:raise ValueError("Assessment unrelated to cohort")
        if not all(a.get(k) for k in ("review_state","editorial_disposition","reason","counterargument","next_test")):raise ValueError("Incomplete review")
        reviews[url]=a
    rows=[]
    for cohort,members in (("OUTSIDE_BUBBLE",sampled),("TOPIC_MATCHED",familiar)):
        for url,item in members.items():
            r=reviews.get(url)
            rows.append({"url":url,"title":item.get("title",""),"cohort":cohort,
                 "review_state":r["review_state"] if r else "NOT_REVIEWED",
                 "editorial_disposition":r["editorial_disposition"] if r else "UNASSESSED",
                 "reason":r["reason"] if r else None,
                 "strongest_objection":r["counterargument"] if r else None,
                 "next_test":r["next_test"] if r else None,
                 "independently_human_labeled":False,
                 "collaborator_identity_verified":False,"outreach_authorized":False})
    reviewed_outside=sum(x["cohort"]=="OUTSIDE_BUBBLE" and x["review_state"] in ("PRIMARY_SOURCE_PREVIOUSLY_REVIEWED","PRIMARY_ABSTRACT_REVIEWED") for x in rows)
    return {"schema":"scout-outside-vs-topic-comparison-v0","rows":rows,
        "outside_sample_count":len(sampled),"familiar_topic_count":len(familiar),
        "editorially_reviewed_outside":reviewed_outside,
        "human_label_coverage":0,
        "precision_recall":"NOT_MEASURABLE_WITHOUT_INDEPENDENT_LABELS",
        "limitations":["Outside sample deliberately biased toward source diversity; not representative of all 50 unmatched leads",
                      "Assistant editor's judgments are not independent ground truth",
                      "Source-identified but not fully read items must not count as source-reviewed confirmations",
                      "No claims of real-world identity matching, adoption or outreach"],
        "publication_authorized":False,"outreach_authorized":False}

def render(data):
    if data.get("schema")!="scout-outside-vs-topic-comparison-v0" or data.get("publication_authorized") is not False or data.get("outreach_authorized") is not False:
        raise ValueError("Private review only")
    e=lambda x:escape(str(x or ""),quote=True)
    h=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout / Discovery Contrast</title>',
    """<style>:root{color-scheme:dark;--bg:#111317;--ink:#f5f5f6;--mute:#bcc0c7;--accent:#e9425a;--line:#444951}*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);margin:0;font:15px/1.65 system-ui,sans-serif}header,main,footer{padding:28px max(20px,calc((100vw - 1100px)/2))}h1{font-size:clamp(38px,6vw,70px);line-height:1.04;letter-spacing:-.055em}h2{font-size:25px;letter-spacing:-.035em}header,footer{border-bottom:1px solid var(--line)}article{border-top:1px solid var(--line);padding:22px 0;display:grid;grid-template-columns:210px 1fr;gap:25px}aside{color:var(--accent);font:700 11px ui-monospace,monospace;overflow-wrap:anywhere}.kicker{color:var(--accent);font:700 11px ui-monospace,monospace;letter-spacing:.15em}.muted{color:var(--mute)}input,select{background:#22262c;color:var(--ink);border:1px solid var(--line);padding:12px;min-height:44px}input{min-width:220px;flex:1}.controls{display:flex;gap:14px;flex-wrap:wrap;margin:24px 0}a{color:inherit;overflow-wrap:anywhere}a:hover{color:var(--accent)}footer{color:var(--mute);border-top:1px solid var(--line);border-bottom:0}@media(max-width:750px){article{grid-template-columns:1fr;gap:5px}}</style>""",
    '</head><body><header><p class="kicker">GHOSTMESH / SCOUT · EDITORIAL CONTRAST</p><h1>What did the filter miss?</h1><p class="muted">Compare outside-bubble sources with familiar-topic matches. All unreviewed cases remain in view. Source-level evidence is distinguished from metadata speculation.</p></header><main>',
    '<p>',str(data["outside_sample_count"]),' outside sources sampled · ',str(data["familiar_topic_count"]),' topic matches · ',str(data["editorially_reviewed_outside"]),' outside records with prior source-level or abstract review · 0 independent human labels.</p>',
    '<div class="controls"><input id="q" type="search" placeholder="Find work or objection" aria-label="Search discoveries"><select id="cohort" aria-label="Cohort"><option value="ALL">Both cohorts</option><option value="OUTSIDE_BUBBLE">Outside interests</option><option value="TOPIC_MATCHED">Topic matched</option></select></div><p id="count" role="status"></p>']
    for row in data["rows"]:
        search=" ".join(str(row.get(k) or "") for k in ("title","reason","strongest_objection"))
        h.extend(['<article data-cohort="',e(row["cohort"]),'" data-search="',e(search.casefold()),'"><aside>',e(row["cohort"].replace("_"," ")),'<p>',e(row["review_state"]),'</p><p>',e(row["editorial_disposition"]),'</p></aside><section><h2>',e(row["title"]),'</h2><p><a href="',e(row["url"]),'" rel="noopener noreferrer" target="_blank">Open original source ↗</a></p>'])
        if row["reason"]:
            h.extend(['<p><strong>Potential connection:</strong> ',e(row["reason"]),'</p><p><strong>Counterargument:</strong> ',e(row["strongest_objection"]),'</p><p><strong>Next test:</strong> ',e(row["next_test"]),'</p>'])
        else:h.append('<p class="muted">NOT REVIEWED. No relevance or surprise conclusion justified.</p>')
        h.append('</section></article>')
    h.extend(['<p class="muted">There is no valid precision or recall estimate: the 21 cases lack independent human labels. Source review is not a collaboration invitation.</p></main><footer>Owner-private draft · No production changes, contact or publication</footer>',
    """<script>const rows=[...document.querySelectorAll('article')],q=document.querySelector('#q'),c=document.querySelector('#cohort');function update(){let n=0;for(const row of rows){let yes=(c.value==='ALL'||row.dataset.cohort===c.value)&&row.dataset.search.includes(q.value.trim().toLowerCase());row.hidden=!yes;if(yes)n++}document.querySelector('#count').textContent=n+' candidate records shown'}q.addEventListener('input',update);c.addEventListener('change',update);update()</script></body></html>"""])
    return "".join(h)

def main():
    p=argparse.ArgumentParser()
    for f in ("outside","triage","editorial","out-json","out-html"):p.add_argument("--"+f,required=True,type=Path)
    a=p.parse_args()
    if a.out_json.exists() or a.out_html.exists():raise SystemExit("Refusing overwrite")
    read=lambda p:json.loads(p.read_text(encoding="utf-8"))
    report=compare(read(a.outside),read(a.triage),read(a.editorial))
    a.out_json.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    a.out_html.write_text(render(report),encoding="utf-8")
    print(json.dumps({"outside":report["outside_sample_count"],"familiar":report["familiar_topic_count"],"editorially_reviewed_outside":report["editorially_reviewed_outside"],"human_labels":report["human_label_coverage"]}))
if __name__=="__main__":main()
