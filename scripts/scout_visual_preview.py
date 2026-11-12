"""Render a one-file owner-private Scout review using real Readers design tokens."""
from __future__ import annotations
import argparse
from html import escape
from pathlib import Path
import json
import re
from scout_editorial_join import join

RECONCILED = {
 "debate": ("INVESTIGATE","Answer diversity is not independent source acquisition; calibration is trained, not a prompted confidence label.","Test 30 fixed claims at equal total tokens: voting, ordinary debate, diversity-selected debate."),
 "sensemaking": ("FOLLOW","Existing GhostMesh provenance may already cover the capability; first establish an actual usability deficit.","Compare 12 real review histories against the existing provenance presentation."),
 "negative-control": ("NO_CONNECTION_JUSTIFIED","Useful Python documentation does not establish a differentiated collaboration thesis.","No connection experiment justified."),
}
CSS = """
:root{color-scheme:dark;--gm-bg:#101215;--gm-paper:#171a1e;--gm-ink:#f4f5f5;--gm-muted:#b4b6bc;--gm-accent:#ed4057;--gm-border:#454851}
html[data-theme=light]{color-scheme:light;--gm-bg:#faf9f7;--gm-paper:#fff;--gm-ink:#17191d;--gm-muted:#545861;--gm-accent:#c8102e;--gm-border:#cfd0d1}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--gm-bg);color:var(--gm-ink);font:16px/1.65 system-ui,-apple-system,sans-serif}
a{color:inherit;text-underline-offset:4px}a:focus-visible,button:focus-visible{outline:2px solid var(--gm-accent);outline-offset:3px}
.gm-site-header{border-bottom:1px solid var(--gm-border);background:var(--gm-paper)}.gm-site-header-inner{max-width:1180px;margin:auto;padding:18px 28px;display:flex;gap:28px;align-items:center;flex-wrap:wrap;justify-content:space-between}
.gm-site-brand{text-decoration:none;font-size:16px;font-weight:800;letter-spacing:.13em}.gm-site-brand em{font-style:normal;color:var(--gm-accent)}.gm-site-brand span{display:block;color:var(--gm-muted);font-size:10px;letter-spacing:.21em}
.gm-site-nav{display:flex;gap:24px;flex-wrap:wrap}.gm-site-nav a{text-decoration:none;font-size:13px;font-weight:700;color:var(--gm-muted)}.gm-site-nav a:hover{color:var(--gm-accent)}
.gm-scout-local-nav{max-width:1180px;margin:auto;padding:18px 28px;border-bottom:1px solid var(--gm-border);display:flex;gap:26px;flex-wrap:wrap;font:700 12px/1.4 system-ui}.gm-scout-local-nav a{text-decoration:none}
.gm-kicker{font:750 12px/1.5 ui-monospace,monospace;text-transform:uppercase;letter-spacing:.13em;color:var(--gm-accent)}
.gm-hero{max-width:1180px;margin:auto;padding:72px 28px 58px;display:grid;grid-template-columns:1.45fr .55fr;gap:55px}
.gm-hero h1{font-size:clamp(42px,6vw,76px);line-height:1.04;letter-spacing:-.065em;margin:9px 0 20px;max-width:14ch}.gm-hero p{max-width:62ch;color:var(--gm-muted)}
.gm-summary{border-top:3px solid var(--gm-accent);padding:20px 0}.gm-summary strong{display:block;font-size:24px;letter-spacing:-.04em}.gm-summary small{color:var(--gm-muted)}
.gm-strands{border-top:1px solid var(--gm-border);border-bottom:1px solid var(--gm-border);max-width:1180px;margin:auto;padding:18px 28px;display:flex;gap:12px;flex-wrap:wrap}
.gm-strands span{font:750 11px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.07em;padding:10px 14px;border:1px solid var(--gm-border)}.gm-strands .active{border-color:var(--gm-accent);color:var(--gm-accent)}
.gm-body{max-width:1180px;padding:38px 28px 85px;margin:auto}.gm-body>h2{font-size:clamp(29px,4vw,48px);letter-spacing:-.05em;margin:10px 0 30px}
.gm-case{border-top:1px solid var(--gm-border);padding:36px 0 44px;display:grid;grid-template-columns:250px minmax(0,1fr);gap:clamp(28px,5vw,65px)}
.gm-case-side{border-top:2px solid var(--gm-accent);padding-top:13px}.gm-case-side .number{font:700 13px ui-monospace,monospace;color:var(--gm-accent)}.gm-case-side p{overflow-wrap:anywhere;font-size:12px;color:var(--gm-muted)}.gm-case-side code{font-size:10px}
.gm-case-main h3{font-size:clamp(24px,3.2vw,39px);letter-spacing:-.04em;line-height:1.12;margin:0 0 14px}.gm-lede{font-size:17px;max-width:65ch}
.gm-judgments{margin-top:28px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}
.gm-judgment{border-top:2px solid var(--gm-border);padding-top:14px}.gm-judgment.final{border-color:var(--gm-accent)}.gm-judgment .tag{font:700 11px ui-monospace,monospace;color:var(--gm-muted);text-transform:uppercase;letter-spacing:.08em}.gm-judgment strong{display:block;margin:12px 0;font-size:16px;overflow-wrap:anywhere}.gm-judgment p{font-size:14px;line-height:1.6;margin:0;color:var(--gm-muted)}
.gm-question{margin:30px 0;border-left:2px solid var(--gm-accent);padding:4px 0 4px 20px}.gm-question strong{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--gm-accent)}
details{border-top:1px solid var(--gm-border);margin-top:22px;padding-top:14px}summary{cursor:pointer;font-weight:700}details p{font-size:14px;color:var(--gm-muted);max-width:78ch}
.gm-footer{background:var(--gm-paper);border-top:1px solid var(--gm-border);padding:40px 28px}.gm-footer-inner{max-width:1180px;margin:auto;display:flex;justify-content:space-between;gap:25px;flex-wrap:wrap}.gm-footer p{font-size:13px;color:var(--gm-muted)}
button.gm-theme{border:1px solid var(--gm-border);background:transparent;color:var(--gm-ink);padding:8px 12px;cursor:pointer;font-weight:700}
@media(max-width:760px){.gm-hero,.gm-case{grid-template-columns:1fr}.gm-hero{padding-top:45px}.gm-judgments{grid-template-columns:1fr}.gm-case-side{max-width:none}}
"""

def render(receipts: Path, editorial: Path)->str:
    join(receipts, editorial)
    data=json.loads(editorial.read_text(encoding="utf-8"))
    if {c["id"] for c in data["cases"]}!=set(RECONCILED):
        raise ValueError("Unrecognized case set")
    manifest=json.loads((receipts/"manifest.json").read_text(encoding="utf-8"))
    src={v["id"]:v for v in manifest["results"]}
    esc=lambda x:escape(str(x),quote=True)
    s=["<!doctype html><html lang='en' data-theme='dark'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow,noarchive'><title>Scout Intelligence | GhostMesh Readers</title><style>",CSS,"</style></head><body>",
       "<header class='gm-site-header'><div class='gm-site-header-inner'><a class='gm-site-brand' href='https://youtube.shareplane.malott.ai/' aria-label='GhostMesh Readers'><strong>GHOST<em>MESH</em></strong><span>READERS</span></a><nav class='gm-site-nav' aria-label='Main'><a href='https://youtube.shareplane.malott.ai/'>Home</a><a href='https://youtube.shareplane.malott.ai/readers/'>Readers</a><a href='https://youtube.shareplane.malott.ai/map/'>Map</a><a href='https://youtube.shareplane.malott.ai/scout/'>Scout</a></nav><button class='gm-theme' type='button' id='theme-toggle' aria-label='Toggle appearance'>LIGHT / DARK</button></div></header>",
       "<nav class='gm-scout-local-nav'><a href='#overview'>Overview</a><a href='#reviews'>Connection theses</a><a href='#method'>Evidence method</a></nav>",
       "<main id='overview'><section class='gm-hero'><div><p class='gm-kicker'>GhostMesh / Scout · Owner-private intelligence</p><h1>Find the signal.<br>Challenge the consensus.</h1><p>Emerging ideas, overlooked connections, and research that matters to GhostMesh. The source remains visible. Disagreement remains part of the record.</p></div><aside class='gm-summary'><p class='gm-kicker'>Research edition / 01</p><strong>3 sources assessed</strong><small>Independent review reconciled · No outreach or publication authorized</small></aside></section>",
       "<div class='gm-strands' aria-label='Scout discovery domains'><span class='active'>Connection intelligence · Pilot</span><span>Attention · Planned</span><span>Research · Planned</span><span>Collaboration · Planned</span><span>Longitudinal · Planned</span></div>",
       "<section id='reviews' class='gm-body'><p class='gm-kicker'>Independent critique / Research records</p><h2>Three discoveries. One useful disagreement.</h2>"]
    for i,case in enumerate(data["cases"],1):
        key=case["id"]; verdict,critique,step=RECONCILED[key]
        pkt=json.loads((receipts/(key+".json")).read_text(encoding="utf-8"))
        title=pkt["substantive_text"].get("title") or "CPython documentation"
        s.extend(["<article class='gm-case'><aside class='gm-case-side'><span class='number'>",f"{i:02} / 03","</span><p>PRIMARY EVIDENCE<br><a href='",esc(src[key]["source_url"]),"' rel='noopener noreferrer'>Open source ↗</a></p><p>SHA-256<br><code>",esc(case["snapshot_sha256"]),"</code></p></aside><div class='gm-case-main'><h3>",esc(title),"</h3><p class='gm-lede'>",esc(case["contribution"]),"</p><div class='gm-judgments'><div class='gm-judgment'><span class='tag'>Initial Scout thesis</span><strong>",esc(case["recommendation"]),"</strong><p>",esc(case["ghostmesh_gap"]),"</p></div><div class='gm-judgment'><span class='tag'>Independent challenge</span><strong>",esc(verdict),"</strong><p>",esc(critique),"</p></div><div class='gm-judgment final'><span class='tag'>Research disposition</span><strong>",esc(verdict),"</strong><p>",esc(step),"</p></div></div><div class='gm-question'><strong>Strongest objection</strong>",esc(case["counterargument"]),"</div><details><summary>Source excerpt and inspection limitations</summary><p>",esc((pkt["substantive_text"].get("excerpt") or "")[:2200]),"</p><p>Snapshot hashes were independently recalculated on VPS. This does not validate authors' empirical claims or collaboration outcomes.</p></details></div></article>"])
    s.extend(["</section><section id='method' class='gm-body'><p class='gm-kicker'>Method / What remains unknown</p><h2>Discovery is a lead, not a verdict.</h2><p>Three topic-selected sources, two apparent agreements and one disagreement. This is not statistically measured accuracy. The reviewer knew the identity of the negative control, and reviewed source pages rather than retained snapshot bytes. No independent experimental reproduction or external contact occurred.</p><p><a href='https://ghostmesh.slack.com/archives/D0C76SEPA3G/p1792722589895059'>Independent review receipt ↗</a></p></section></main><footer class='gm-footer'><div class='gm-footer-inner'><strong>GHOSTMESH / READERS / SCOUT</strong><p>Read the source. Challenge the interpretation. Context endures.</p></div></footer>",
              "<script>document.getElementById('theme-toggle').addEventListener('click',()=>{const root=document.documentElement;root.dataset.theme=root.dataset.theme==='light'?'dark':'light'})</script></body></html>"])
    return "".join(s)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--receipts",type=Path,required=True);ap.add_argument("--editorial",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args()
    if a.out.exists(): raise SystemExit("Refusing overwrite")
    a.out.write_text(render(a.receipts,a.editorial),encoding="utf-8");print(a.out)
if __name__=="__main__":main()
