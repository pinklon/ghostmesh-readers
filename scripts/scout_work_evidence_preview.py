"""Attach a source-work evidence note to the private People & Builders view.

This annotation applies to the paper, never to the named authors' character,
expertise, identities, or willingness to collaborate.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from html import escape

def render(people_html:str,annotation:dict,ablation:dict)->str:
    if "<!doctype html>" not in people_html.lower() or "</main>" not in people_html:
        raise ValueError("Invalid People view")
    if "noindex,nofollow" not in people_html:
        raise ValueError("Missing private metadata")
    if annotation.get("schema")!="scout-reviewed-work-annotations-v0" or ablation.get("schema")!="scout-failure-ledger-ablation-v0":
        raise ValueError("Wrong research payload")
    if annotation.get("contact_authorized") is not False or annotation.get("publication_authorized") is not False:
        raise ValueError("Work annotation cannot authorize contact or publication")
    if ablation.get("outreach_authorized") is not False or ablation.get("publication_authorized") is not False:
        raise ValueError("Experiment cannot authorize contact or publication")
    s=ablation["summary"]
    for k in ("ledger","no_ledger"):
        if k not in s:raise ValueError("Incomplete paired trial")
    e=lambda x:escape(str(x),quote=True)
    panel=f"""<section style="border-top:3px solid var(--accent);padding-top:24px;margin:48px 0" id="work-evidence">
<p class="kicker">Selected work / Evidence and counterevidence</p>
<h2 style="font-size:clamp(26px,4vw,42px);letter-spacing:-.05em">SpecEvo-inspired experiment</h2>
<p><strong>Paper:</strong> <a href="{e(annotation['source_work'])}" rel="noopener noreferrer">{e(annotation['work_title'])} ↗</a></p>
<p><strong>Research status:</strong> {e(annotation['disposition'])}. This is a provisional work-level assessment, not a judgment of its authors.</p>
<p><strong>Controlled ablation:</strong> 144 paired synthetic trials for each arm; identical proposal tapes and evaluation budgets.</p>
<table style="width:100%;border-collapse:collapse;text-align:left"><thead><tr><th>Policy</th><th>Mean best reward</th><th>Exact solutions</th><th>Duplicate evaluations</th><th>Proposals examined</th></tr></thead><tbody>
"""
    for key,label in (("no_ledger","No ledger"),("ledger","Failure ledger")):
        x=s[key]
        panel+="<tr>"+ "".join("<td style='border-top:1px solid var(--line);padding:10px 6px'>"+e(v)+"</td>" for v in (label,x["mean_best_reward"],x["exact_matches"],x["duplicate_evaluations"],x["total_proposals_examined"]))+"</tr>"
    panel+="""</tbody></table>
<p><strong>Strongest limitation:</strong> This isolates avoiding duplicate evaluations on a fixed proposal tape. It does not test memory-guided reasoning, real models, scientific discovery, or privileged agent execution. The ledger also incurs proposal-inspection overhead.</p>
<p><strong>Next research question:</strong> Does richer failure guidance improve decisions beyond simple duplicate avoidance when proposal and guidance costs are both counted?</p>
<p><strong>Contact:</strong> Not authorized. <strong>Independent replication:</strong> Not performed.</p></section>"""
    return people_html.replace("</main>",panel+"</main>",1)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("people","annotation","ablation","out"):p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refuse overwrite")
    read=lambda x:json.loads(x.read_text(encoding="utf-8"))
    a.out.write_text(render(a.people.read_text(encoding="utf-8"),read(a.annotation),read(a.ablation)),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
