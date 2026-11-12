"""Show source-revision reconciliation receipts inside existing private History view."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from html import escape

def render(history_html, reconciliation):
    if "noindex,nofollow" not in history_html or "</main>" not in history_html:
        raise ValueError("Private history page required")
    if reconciliation.get("schema")!="scout-reconciliation-v0":
        raise ValueError("Wrong reconciliation schema")
    if reconciliation.get("publication_authorized") is not False or reconciliation.get("outreach_authorized") is not False:
        raise ValueError("No publish or outreach")
    receipts=reconciliation.get("ingestion_receipts")
    summary=reconciliation.get("ingestion_summary")
    if not isinstance(receipts,list) or not isinstance(summary,dict):
        raise ValueError("Ledger receipts required")
    counts={"ACCEPTED":0,"DUPLICATE_REVISION":0,"SEEN_AGAIN_UNVERIFIED":0}
    for entry in receipts:
        state=entry.get("state")
        if state not in counts or entry.get("outreach_authorized") is not False:
            raise ValueError("Untrusted receipt")
        counts[state]+=1
    if (counts["ACCEPTED"]!=summary.get("accepted") or
        counts["DUPLICATE_REVISION"]!=summary.get("duplicate_revisions") or
        counts["SEEN_AGAIN_UNVERIFIED"]!=summary.get("unverified_reobservations")):
        raise ValueError("Receipt totals inconsistent")
    e=lambda x:escape(str(x or ""),quote=True)
    html=['<section id="ledger-receipts" style="margin:32px auto;max-width:1080px;padding:25px;border:1px solid #666">',
          '<h2>Source ledger and recovery receipts</h2>',
          '<p>Additional source evidence is accepted independently of publication timestamp. Unknown revisions are never silently treated as verified identical content.</p>',
          '<p><strong>',str(counts["ACCEPTED"]),'</strong> newly accepted; <strong>',
          str(counts["DUPLICATE_REVISION"]),'</strong> duplicate known revisions; <strong>',
          str(counts["SEEN_AGAIN_UNVERIFIED"]),'</strong> previously observed sources without independently verified revision bytes.</p>',
          '<details><summary>Inspect reconciliation receipts</summary><div style="max-height:380px;overflow:auto">']
    for item in receipts:
        html.extend(['<p><strong>',e(item["state"]),'</strong> · ',e(item["source_identity"]),
                     ' · revision ',e(item.get("revision") or "UNVERIFIED"),
                     ' · identity ',e(item["person_identity"]),'</p>'])
    html.extend(['</div></details><p style="opacity:.75;font-size:13px">A repeated unversioned link is not proof content remained unchanged. No person identity is inferred from an author name.</p></section>'])
    return history_html.replace("</main>","".join(html)+"</main>",1)

def main():
    p=argparse.ArgumentParser()
    for key in ("history","reconciliation","out"):p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    a.out.write_text(render(a.history.read_text(encoding="utf-8"),json.loads(a.reconciliation.read_text(encoding="utf-8"))),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
