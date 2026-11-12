"""Render a compact owner-private stepwise Scout replay report from fixed receipts."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from html import escape

def render(report):
    if report.get("schema")!="scout-stepwise-counterfactual-v0":
        raise ValueError("Unexpected replay schema")
    if report.get("publication_authorized") is not False or report.get("outreach_authorized") is not False:
        raise ValueError("Research only")
    if not report.get("pairs") or not report.get("summary"):raise ValueError("Missing replay evidence")
    e=lambda x:escape(str(x),quote=True)
    css="""<style>:root{color-scheme:dark;--bg:#101215;--ink:#f1f2f3;--muted:#babdc3;--line:#474a50;--accent:#ed465c;--surface:#191c20}*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);margin:0;font:15px/1.55 system-ui,-apple-system,sans-serif}header,main,footer{padding:28px max(20px,calc((100vw - 1120px)/2))}header,footer{border-bottom:1px solid var(--line)}.kicker{font:700 11px ui-monospace,monospace;color:var(--accent);letter-spacing:.16em;text-transform:uppercase}h1{font-size:clamp(36px,5.5vw,68px);line-height:1.04;letter-spacing:-.05em;margin:10px 0}h2{font-size:26px;letter-spacing:-.03em}p{max-width:77ch}small,.muted{color:var(--muted)}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;min-width:700px}th,td{padding:11px;border-bottom:1px solid var(--line);text-align:left}th{color:var(--muted);font-size:12px}tr[data-alert=true]{border-left:3px solid var(--accent)}.split{display:grid;grid-template-columns:1fr 1fr;gap:18px}.pane{border:1px solid var(--line);padding:18px;overflow:auto;background:var(--surface)}.tag{color:var(--accent);font:700 11px ui-monospace,monospace;letter-spacing:.08em}code{color:var(--muted)}select{background:var(--surface);color:var(--ink);border:1px solid var(--line);padding:10px;min-width:220px}select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}footer{border-top:1px solid var(--line);border-bottom:0;font-size:12px}@media(max-width:800px){.split{grid-template-columns:1fr}}</style>"""
    html=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>Scout | Stepwise Replay</title>',css,'</head><body><header><div class="kicker">GHOSTMESH / SCOUT · Offline research</div><h1>Decision traces,<br>not just verdicts.</h1><p class="muted">Matched synthetic policy replays, with each action preceded by what the policy could observe. No stronger model was called, and no real agent was stopped.</p></header><main><h2>Paired outcomes</h2><div class="scroll"><table><thead><tr><th>Injected error rate</th><th>Policy</th><th>Exact solutions / 144</th><th>Mean best reward</th><th>Mean cost (toy units)</th><th>Mean proposals examined</th></tr></thead><tbody>']
    for row in report["summary"]:
        html.extend(['<tr><td>',e(round(row["error_rate"]*100)),'%</td><td>',e(row["policy"]),'</td><td>',e(row["exact_matches"]),'</td><td>',e(row["mean_best_reward"]),'</td><td>',e(row["mean_cost_units"]),'</td><td>',e(row["mean_proposals"]),'</td></tr>'])
    html.extend(['</tbody></table></div><h2>Inspect a paired trace</h2><p class="muted">Choose the simulated noise level. The same first task and seed are replayed under both policies. These are illustrative, not cherry-picked for a winning outcome.</p><label class="tag" for="rate">FEEDBACK ERROR RATE</label> <select id="rate">'])
    for rate in (0,0.1,0.3,0.5):html.extend(['<option value="',str(rate),'">',str(int(rate*100)),'% incorrect hints</option>'])
    html.append('</select><div class="split">')
    for policy,title in (("ledger","Independent baseline"),("adaptive","Adaptive guidance")):
        html.append('<section class="pane"><h2>'+e(title)+'</h2><div id="trace-'+policy+'"></div></section>')
    html.append('</div><p class="muted">Interpretation: the adaptive arm receives extra, potentially incorrect information. The baseline does not. A higher reward is not an equal-information victory; proposal inspection and hints cost extra.</p></main><footer>Private prototype · Synthetic evidence · No production authority, publication or outreach</footer>')
    sample={}
    for pair in report["pairs"]:
        if pair["task"]==0 and pair["seed"]==0:
            sample[str(pair["injected_noise"])]={
                p:[{"step":x["before_decision"]["step"]+1,"prior_best":x["before_decision"]["best_reward_so_far"],"action":x["action"],"candidate":x["observed_candidate"],"reward":x["observed_reward"],"hint":x["observed_hint"],"proposals":x["proposals_examined_after"]} for x in pair[p]["trace"]] for p in ("ledger","adaptive")}
    safe=json.dumps(sample,separators=(",",":")).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    html.append('<script>const samples='+safe+';function show(){const data=samples[document.querySelector("#rate").value];for(const policy of ["ledger","adaptive"]){const el=document.querySelector("#trace-"+policy);el.replaceChildren();for(const x of (data?.[policy]||[])){const p=document.createElement("p");const b=document.createElement("strong");b.textContent="Step "+x.step+": "+x.action;p.append(b,document.createTextNode(" | prior best "+x.prior_best+", candidate "+x.candidate+", observed reward "+x.reward+(x.hint?", hint "+x.hint:"")+", proposals examined "+x.proposals));el.append(p)}}}document.querySelector("#rate").addEventListener("change",show);show();</script></body></html>')
    return "".join(html)

def main():
    p=argparse.ArgumentParser()
    for k in ("report","out"):p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    a.out.write_text(render(json.loads(a.report.read_text())),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
