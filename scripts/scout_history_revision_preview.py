"""Overlay separately witnessed upstream revision evidence onto the private Scout timeline.

Every revision receipt is explicitly scoped to its source identity; content impact is never
inferred from file names or patches. No public deployment, network access, or outreach.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from html import escape
from scout_history_preview import render as history_render

STYLE = """
.gm-revision-list{border-top:2px solid var(--accent);margin:24px 0 50px}
.gm-revision{display:grid;grid-template-columns:190px minmax(0,1fr);gap:28px;padding:27px 0;border-bottom:1px solid var(--line)}
.gm-revision h3{font-size:clamp(20px,2.8vw,30px);line-height:1.2;letter-spacing:-.035em;margin:0 0 12px}
.gm-revision a{overflow-wrap:anywhere}.gm-revision code{overflow-wrap:anywhere;font-size:12px}
.gm-revision details{border-top:1px solid var(--line);padding-top:13px;margin-top:17px}
.gm-revision summary{cursor:pointer;font-weight:750}
.gm-revision li{padding:8px 0;border-bottom:1px solid var(--line);font-size:14px;overflow-wrap:anywhere}
.gm-revision .class{display:inline-block;border:1px solid var(--line);padding:5px 8px;margin:4px 6px 4px 0;font:700 11px ui-monospace,monospace}
.gm-revision .explanation{font-size:14px;color:var(--muted)}
@media(max-width:730px){.gm-revision{grid-template-columns:1fr;gap:8px}}
"""

def file_hint(path: str) -> str:
    """A review-routing hint, never a semantic classification."""
    p=path.lower()
    if p.endswith((".md",".rst",".txt")) or "/docs/" in p or "/news" in p:
        return "DOCUMENTATION_OR_RELEASE_NOTE_CANDIDATE"
    if p.endswith((".py",".c",".h",".rs",".go",".js",".ts")):
        return "IMPLEMENTATION_OR_TEST_CANDIDATE"
    return "OTHER_FILE_CANDIDATE"

def render(history: dict, relations: dict, evidence: list[dict]) -> str:
    original=history_render(history,relations)
    if not original.endswith("</html>"):
        raise ValueError("Malformed base preview")
    fragments=["<section class='notice' id='revision-evidence'><p class='kicker'>Version witness / Separate primary-source evidence</p>",
               "<h2>Changed upstream. Meaning still under review.</h2>",
               "<p class='muted'>These revision receipts are not the same as feed appearances. They describe exact upstream revisions. Changed paths and extracted text identify places worth reading, not validated advances or conclusions.</p>",
               "<div class='gm-revision-list'>"]
    esc=lambda s:escape(str(s if s is not None else ""),quote=True)
    for item in evidence:
        if item.get("publication_authorized") is not False or item.get("outreach_authorized") is not False:
            raise ValueError("Source evidence carries unauthorized permissions")
        schema=item.get("schema")
        if schema=="scout-github-change-evidence-v0":
            identity=item["identity"]; before=item["before_revision"]; after=item["after_revision"]
            files=item.get("files",[])
            if not isinstance(files,list): raise ValueError("Bad file list")
            categories={}
            for f in files:
                hint=file_hint(f["path"])
                categories[hint]=categories.get(hint,0)+1
            fragments.extend(["<article class='gm-revision'><aside><span class='kicker'>GitHub commit comparison</span><p class='muted'>Exact upstream revision evidence</p></aside><div>",
                              "<h3>",esc(identity),"</h3><p><code>",esc(before[:12]),"</code> → <code>",esc(after[:12]),"</code></p>",
                              "<p class='explanation'>",str(len(files))," paths returned. Provider comparison: ",esc(item.get("provider_status","UNKNOWN")),
                              ". Technical significance: NOT EVALUATED.</p>"])
            for name,n in sorted(categories.items()):
                fragments.extend(["<span class='class'>",esc(name.replace("_"," ")),": ",str(n),"</span>"])
            fragments.extend(["<details><summary>Inspect changed paths</summary><ul>"])
            for f in files[:100]:
                fragments.extend(["<li><strong>",esc(f["path"]),"</strong> · ",esc(f.get("status","UNKNOWN")),
                                  " · candidate route: ",esc(file_hint(f["path"])),"</li>"])
            fragments.extend(["</ul></details>",
                              "<p class='explanation'>File categories are extension-based review hints only. No source code was executed or change significance adjudicated.</p></div></article>"])
        elif schema=="scout-arxiv-revision-evidence-v0":
            fragments.extend(["<article class='gm-revision'><aside><span class='kicker'>arXiv revision</span></aside><div>",
                              "<h3>",esc(item["identity"]),"</h3><p>",esc(item["revision"]),"</p>",
                              "<p>Text comparison: ",esc(item.get("status","NOT_EVALUATED")),"</p></div></article>"])
        else:
            raise ValueError("Unexpected revision evidence schema")
    fragments.extend(["</div><p class='muted'>No automatic thesis reversals, no verified scientific claims, and no production authority.</p></section>"])
    insert="".join(fragments)
    original=original.replace("</style>","\n"+STYLE+"</style>",1)
    original=original.replace("</main>",insert+"</main>",1)
    if "<section class='notice' id='revision-evidence'>" not in original:
        raise ValueError("Revision section insertion failed")
    return original

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ("history","relations","evidence","out"):
        p.add_argument("--"+field,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise SystemExit("Refusing overwrite")
    load=lambda x:json.loads(x.read_text(encoding="utf-8"))
    output=render(load(a.history),load(a.relations),[load(x) for x in a.evidence.glob("*.json")])
    a.out.write_text(output,encoding="utf-8")
    print(a.out)

if __name__=="__main__":main()
