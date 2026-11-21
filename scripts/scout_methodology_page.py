"""Render a private, evidence-aware Scout methodology page for a specific run.

Use the repository methodology as the detailed canonical explanation, and
populate collection health from the run rather than claiming all feeds worked.
"""
from __future__ import annotations
from collections import Counter
from html import escape
from pathlib import Path
from scout_signal_intake import FEEDS,GITHUB_QUERIES,HN_URL,API_GITHUB

def render_methodology(intake,methodology_text):
    if intake.get("schema")!="scout-multisource-intake-v0" or intake.get("publication_authorized") is not False or intake.get("outreach_authorized") is not False:
        raise ValueError("Research-only source data required")
    if "## End-to-end signal path" not in methodology_text or "## Current implementation reality" not in methodology_text:
        raise ValueError("Expected complete source methodology document")
    diagnostics=intake.get("diagnostics",[])
    if not isinstance(diagnostics,list):raise ValueError("Invalid source diagnostics")
    states=Counter(x.get("state") for x in diagnostics)
    count=len(intake.get("sampled_leads",[]))
    e=lambda x:escape(str(x or ""),quote=True)
    names=[]
    for source,(url,lane) in FEEDS.items():
        names.append((source,lane,url))
    for term in GITHUB_QUERIES:
        names.append(("github:"+term,"code",API_GITHUB+"?q="+term.replace(" ","+")))
    names.extend((("hacker-news","attention",HN_URL),("dev-community","creator","https://dev.to/api/articles?tag=ai")))
    rows=[]
    diagnostic_by_name={x.get("source"):x for x in diagnostics}
    for source,lane,url in names:
        d=diagnostic_by_name.get(source,{})
        rows.append("<tr><td>"+e(source)+"</td><td>"+e(lane)+"</td><td><a rel='noopener noreferrer' target='_blank' href='"+e(url)+"'>Public endpoint ↗</a></td><td>"+e(d.get("state","NOT_OBSERVED"))+"</td><td>"+e(d.get("items","—"))+"</td></tr>")
    # Keep every part of the approved explanation readable offline, without
    # executing Markdown, remote scripts or arbitrary HTML from external sources.
    page="""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow,noarchive'><title>Scout / How signals enter</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{background:#111419;color:#f1f2f4;font:15px/1.7 system-ui,sans-serif;margin:0}main,header,footer{max-width:1160px;margin:auto;padding:28px 25px}header{border-bottom:1px solid #545760}h1{font-size:clamp(36px,6vw,67px);line-height:1.1;letter-spacing:-.04em}h2{font-size:26px}.kicker{font:700 11px ui-monospace,monospace;color:#fa526c;letter-spacing:.14em}.muted{color:#b9c0c9}.numbers{display:flex;flex-wrap:wrap;gap:30px;border-block:1px solid #545760;padding:20px 0}.numbers strong{font-size:35px;display:block}table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;border-bottom:1px solid #545760;padding:12px 9px;overflow-wrap:anywhere}a{color:#f8a4b3}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 system-ui,sans-serif;background:#1b2028;border:1px solid #545760;border-radius:12px;padding:24px}summary{cursor:pointer;font-weight:800;font-size:20px;padding:14px 0}footer{border-top:1px solid #545760;color:#b9c0c9}@media(max-width:650px){.tablewrap{overflow-x:auto}table{min-width:680px}}</style></head><body><header><p class='kicker'>GHOSTMESH / SCOUT · METHODOLOGY</p><h1>How we find the signal.</h1><p>Every source, every decision boundary, every important uncertainty. The methodology is readable without logging in or trusting a black box.</p><p class='muted'>Run data is private. Source links point to original public endpoints.</p></header><main><section><h2>This run at a glance</h2><div class='numbers'><div><strong>"""+str(count)+"""</strong>Public observations</div><div><strong>"""+str(len(diagnostics))+"""</strong>Streams attempted</div><div><strong>"""+str(states.get("FETCHED",0))+"""</strong>Streams fetched</div><div><strong>"""+str(states.get("ERROR",0))+"""</strong>Failed streams</div></div><p class='muted'>Capture timestamp: """+e(intake.get("captured_utc","UNKNOWN"))+"""</p><p>Observations are not verified claims, unique people, measured trends or collaboration endorsements. Top-N sampling can miss work.</p></section><section><h2>Public retrieval endpoints and actual run status</h2><div class='tablewrap'><table><thead><tr><th>Stream</th><th>Lane</th><th>Source</th><th>State</th><th>Items</th></tr></thead><tbody>"""+ "".join(rows)+"""</tbody></table></div></section><section><details open><summary>Complete methodology and limitations</summary><p>The following canonical research explanation is included verbatim as escaped text. It describes source selection, sampling, URL identity, evidence review, source bias, permission controls, and how conclusions can be challenged.</p><pre>"""+e(methodology_text)+"""</pre></details></section></main><footer>Owner-private research artifact. Public methodological explanation does not authorize publishing private run data or contacting anyone.</footer></body></html>"""
    return page

def canonical_document():
    path=Path(__file__).resolve().parents[1]/"research"/"SCOUT-METHODOLOGY.md"
    return path.read_text(encoding="utf-8")
