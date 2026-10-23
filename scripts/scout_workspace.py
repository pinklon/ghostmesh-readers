"""Build a single private Scout workspace from previously qualified static views.

No network access, no service, no publication. Keep all source previews embedded
as sandboxed srcdoc panels; the workspace shell owns navigation only.
"""
from __future__ import annotations
import argparse
from html import escape
from pathlib import Path

SECTIONS=(("Discover","discovery"),("Relationships","relationships"),("History & revisions","history"),("Claim impact","claims"),("People & builders","people"),("Decision replay","replay"),("Connection theses","theses"),("Public trails","trails"),("Capability differences","differences"))

def build(files:dict[str,str])->str:
    if set(files)!={key for _,key in SECTIONS}: raise ValueError("Nine private views required")
    for key,text in files.items():
        if not text.lstrip().lower().startswith("<!doctype html>") or "</html>" not in text.lower():
            raise ValueError("Invalid HTML view "+key)
        if "noindex,nofollow" not in text:
            raise ValueError("Private metadata missing")
    tabs="".join(f'<button type="button" role="tab" id="tab-{key}" aria-controls="panel-{key}" aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}" data-view="{key}">{escape(label)}</button>' for i,(label,key) in enumerate(SECTIONS))
    frames=[]
    for i,(label,key) in enumerate(SECTIONS):
        # Using srcdoc HTML-attribute escaping prevents an input document from
        # breaking out of its sandboxed frame into the shell document.
        frames.append(f'<section role="tabpanel" id="panel-{key}" aria-labelledby="tab-{key}" {"hidden" if i else ""}><iframe title="{escape(label)}" sandbox="allow-scripts allow-popups" referrerpolicy="no-referrer" loading="lazy" srcdoc="{escape(files[key],quote=True)}"></iframe></section>')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>GhostMesh Scout | Private Workspace</title>
<style>:root{color-scheme:dark;font-family:system-ui,-apple-system,sans-serif}*{box-sizing:border-box}body{margin:0;background:#101215;color:#eee}header{display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;padding:18px max(22px,calc((100vw - 1200px)/2));border-bottom:1px solid #45474c}header strong{letter-spacing:.14em}header em{font-style:normal;color:#e83b52}header small{display:block;color:#a5aab4;font:700 10px ui-monospace,monospace;letter-spacing:.14em}nav{display:flex;flex-wrap:wrap;gap:9px;padding:12px max(22px,calc((100vw - 1200px)/2));border-bottom:1px solid #45474c}button{cursor:pointer;border:1px solid #45474c;padding:11px 15px;background:transparent;color:#e5e8ed;font-weight:700}button[aria-selected=true]{border-color:#e83b52;border-bottom:3px solid #e83b52}button:focus-visible{outline:2px solid #ed5364;outline-offset:3px}section[hidden]{display:none}iframe{border:0;width:100%;height:calc(100vh - 157px);min-height:600px;display:block}footer{padding:12px 22px;color:#b3b8c0;font-size:12px;border-top:1px solid #45474c}</style></head>
<body><header><div><strong>GHOST<em>MESH</em> / SCOUT</strong><small>PRIVATE INTELLIGENCE WORKSPACE</small></div><small>Discovery → Connections → History → Claims → People</small></header><nav role="tablist" aria-label="Scout views">'''+tabs+'''</nav><main>'''+''.join(frames)+'''</main><footer>Research only · Source evidence is not verified scientific truth · No outreach or publication authority</footer><script>
const buttons=[...document.querySelectorAll('[role=tab]')];function selectTab(button){for(const b of buttons){let active=b===button;b.setAttribute('aria-selected',active?'true':'false');b.tabIndex=active?0:-1;document.getElementById('panel-'+b.dataset.view).hidden=!active;}button.focus();}
for(const b of buttons){b.addEventListener('click',()=>selectTab(b));b.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();let i=buttons.indexOf(b),dir=e.key==='ArrowRight'?1:-1;selectTab(buttons[(i+dir+buttons.length)%buttons.length]);}});}
</script></body></html>'''

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for label,key in SECTIONS:p.add_argument("--"+key,required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing to overwrite existing workspace")
    a.out.write_text(build({key:getattr(a,key).read_text(encoding="utf-8") for _,key in SECTIONS}),encoding="utf-8")
    print(a.out)
if __name__=="__main__":main()
