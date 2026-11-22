"""Render exact-source Scout claim impact as an owner-private HTML review pane."""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path

def render(impact,register):
    if impact.get("schema")!="scout-claim-impact-v0" or register.get("schema")!="scout-claim-register-v0":
        raise ValueError("Unexpected claim schema")
    if any(x.get("publication_authorized") is not False or x.get("outreach_authorized") is not False for x in (impact,register)):
        raise ValueError("Private-only claim evidence required")
    claims={x["id"]:x for x in register["claims"]}
    findings=impact["observations"]
    if len(findings)!=len(claims) or {x["claim_id"] for x in findings}!=set(claims):
        raise ValueError("Claim impact coverage mismatch")
    esc=lambda x:escape(str(x if x is not None else ""),quote=True)
    parts=['<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | Claim Impact</title>',
    """<style>:root{color-scheme:dark;--bg:#101215;--ink:#f1f1f1;--muted:#b6b9bf;--accent:#ef4558;--line:#44474d;--paper:#1b1e23}html[data-theme=light]{color-scheme:light;--bg:#faf9f7;--ink:#191a1d;--muted:#545963;--accent:#be1938;--line:#d2d2d2;--paper:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,sans-serif}main,header,footer{padding:30px max(22px,calc((100vw - 1100px)/2))}header{border-bottom:1px solid var(--line)}.kicker{font:750 11px/1.5 ui-monospace,monospace;text-transform:uppercase;letter-spacing:.14em;color:var(--accent)}h1{font-size:clamp(42px,6vw,74px);letter-spacing:-.06em;line-height:1.04;margin:10px 0 20px}h2{font-size:clamp(25px,3vw,37px);letter-spacing:-.04em;line-height:1.14;margin:7px 0 17px}p{max-width:75ch}.lede,.muted{color:var(--muted)}.stats{display:flex;flex-wrap:wrap;gap:36px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:21px 0;margin:38px 0}.stats strong{display:block;font-size:30px;letter-spacing:-.04em}.stats small{color:var(--muted);font:700 11px ui-monospace,monospace;text-transform:uppercase}.claim{border-top:2px solid var(--line);padding:29px 0 36px;display:grid;grid-template-columns:200px 1fr;gap:33px}.claim.review{border-top-color:var(--accent)}.sidebar{font:700 11px/1.8 ui-monospace,monospace;color:var(--muted);overflow-wrap:anywhere}.sidebar strong{display:block;color:var(--accent)}.status{display:inline-block;padding:6px 9px;border:1px solid var(--line);font:750 11px ui-monospace,monospace;letter-spacing:.04em;margin-bottom:15px}.claim p{margin:10px 0;color:var(--muted)}.claim p strong{color:var(--ink)}a{color:inherit;text-underline-offset:4px}a:hover{color:var(--accent)}footer{border-top:1px solid var(--line);font-size:13px;color:var(--muted)}button{background:var(--paper);border:1px solid var(--line);padding:10px;color:var(--ink);cursor:pointer}button:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:3px}@media(max-width:730px){.claim{grid-template-columns:1fr;gap:12px}}</style>""",
    '</head><body><header><p class="kicker">GHOSTMESH / SCOUT · Private intelligence</p><h1>Which conclusions<br>need another look?</h1><p class="lede">Each claim is linked to a specific upstream revision. A changed version requests review; it never silently changes the underlying judgment.</p><button type="button" id="theme">LIGHT / DARK</button></header><main><div class="stats">',
    '<div><strong>'+str(impact["counts"]["claims"])+'</strong><small>Tracked claims</small></div>',
    '<div><strong>'+str(impact["counts"]["matched"])+'</strong><small>Revision matches</small></div>',
    '<div><strong>'+str(impact["counts"]["revision_review"])+'</strong><small>Revision review required</small></div></div>']
    for entry in findings:
        claim=claims[entry["claim_id"]]
        if (entry["source_identity"]!=claim["source_identity"] or
            entry["pinned_revision"]!=claim["source_revision"] or
            entry["editorial_disposition"]!=claim["disposition"] or
            entry.get("disposition_changed") is not False):
            raise ValueError("Claim identity or editorial state mismatch")
        status=entry["state"]
        if status not in {"REVISION_MATCH","REVIEW_SOURCE_REVISION","NO_CURRENT_WITNESS"}:raise ValueError("Unknown review status")
        parts.extend(['<article class="claim '+('review' if status!="REVISION_MATCH" else '')+'">',
            '<aside class="sidebar"><strong>REVISION EVIDENCE</strong>',esc(claim["source_identity"]),'<p>PINNED: ',esc(claim["source_revision"]),'</p><p>OBSERVED: ',esc(entry.get("observed_revision") or "UNKNOWN"),'</p></aside><section>',
            '<span class="status">',esc(status.replace("_"," ")),'</span><h2>',esc(entry["claim_id"].replace("-"," ").title()),'</h2>',
            '<p><strong>Source-reported:</strong> ',esc(claim["claim"]),'</p>',
            '<p><strong>GhostMesh interpretation:</strong> ',esc(claim["editorial_interpretation"]),'</p>',
            '<p><strong>Current editorial decision:</strong> ',esc(claim["disposition"]),'</p>',
            '<p><strong>Next action:</strong> ',esc(entry["recommended_action"].replace("_"," ").title()),'</p>',
            '<p><a href="',esc(claim["source_url"]),'">Read pinned source ↗</a></p></section></article>'])
    parts.extend(['<p class="muted">These revisions establish source identity, not empirical correctness. Reviews remain human decisions, even when upstream bytes or versions change.</p></main><footer>Private research only · No automatic editorial change · No public release or outreach</footer>',
     """<script>document.getElementById('theme').addEventListener('click',()=>{const x=document.documentElement;x.dataset.theme=x.dataset.theme==='light'?'dark':'light'});</script></body></html>"""])
    return "".join(parts)

def main():
    p=argparse.ArgumentParser()
    for key in ("impact","register","out"):p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    read=lambda x:json.loads(x.read_text(encoding="utf-8"))
    a.out.write_text(render(read(a.impact),read(a.register)),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
