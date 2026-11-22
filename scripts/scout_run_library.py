"""Generate an owner-private, read-only Scout run library page.

Only manifest-verified runs are linked. The output is separate from the run root
so inventory never confuses a navigation page with an immutable research run.
No scheduler, network access, deletion, or public deployment.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from html import escape
from scout_private_archive import inventory

def build(root,out):
    root=Path(root).resolve()
    out=Path(out).resolve()
    if out.exists():
        raise FileExistsError("Refusing to replace an existing run library")
    if root==out.parent or root in out.parents:
        raise ValueError("Run library must live outside the immutable run root")
    report=inventory(root)
    rows=report["runs"]
    if any(r["integrity"]!="VERIFIED" for r in rows):
        raise ValueError("Unverified run present; do not promote the index")
    rows=sorted(rows,key=lambda r:(r.get("captured_utc") or "",r["run_id"]),reverse=True)
    e=lambda s:escape(str(s if s is not None else ""),quote=True)
    cards=[]
    for item in rows:
        run=root/item["run_id"]
        manifest=json.loads((run/"manifest.json").read_text(encoding="utf-8"))
        relative=os.path.relpath(run/"workspace.html",out.parent)
        if relative.startswith("../") and not (run/"workspace.html").is_file():
            raise ValueError("Missing workspace")
        if not (run/"workspace.html").is_file():
            raise ValueError("Missing workspace")
        health=manifest.get("sources",[])
        failed=sum(x.get("state")!="FETCHED" for x in health)
        available=sum(x.get("state")=="FETCHED" for x in health)
        hist=manifest.get("workspace_view_status",{}).get("history","UNKNOWN")
        cards.extend(["<article><div class='label'>",e(item["run_id"]),"</div>",
                      "<h2><a href='",e(relative),"'>Open private Scout workspace ↗</a></h2>",
                      "<p>Captured ",e(item.get("captured_utc") or "UNKNOWN"),"</p>",
                      "<div class='counts'><span><strong>",str(item.get("leads") or 0),"</strong> public leads</span>",
                      "<span><strong>",str(manifest.get("candidate_count") or 0),"</strong> reading candidates</span>",
                      "<span><strong>",str(available),"</strong> streams fetched</span>",
                      "<span><strong>",str(failed),"</strong> source errors</span></div>",
                      "<p>History: ",e(hist)," · Artifact integrity: verified</p></article>"])
    page=("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
          "<meta name='viewport' content='width=device-width,initial-scale=1'>"
          "<meta name='robots' content='noindex,nofollow,noarchive'>"
          "<title>GhostMesh Scout | Private Run Library</title>"
          "<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101215;color:#f5f5f5;font:15px/1.6 system-ui,sans-serif}header,main,footer{max-width:1120px;padding:28px;margin:auto}h1{font-size:clamp(36px,6vw,64px);line-height:1.05;letter-spacing:-.05em}article{border-top:1px solid #555;padding:20px 0}.label{font:700 12px monospace;color:#f07688}h2{font-size:26px}a{color:#ffb5c0}.counts{display:flex;flex-wrap:wrap;gap:22px}.counts strong{font-size:26px;display:block}p,footer{color:#bbc0c7}footer{border-top:1px solid #555}</style></head><body>"
          "<header><p class='label'>GHOSTMESH / SCOUT · OWNER-PRIVATE</p>"
          "<h1>Every run. Its evidence. Its limits.</h1>"
          "<p>This page links only to independently checksum-verified private research runs. The newest capture appears first. "
          "Collection is manual and no review status implies a verified source claim or real-world identity.</p></header>"
          "<main>"+("".join(cards) if cards else "<p>No recorded Scout runs yet.</p>")+"</main>"
          "<footer>Generated read-only from private run manifests. No scheduled collection, automatic deletion, publication or contributor outreach.</footer></body></html>")
    return page,{"verified_runs":len(rows),"latest_run":rows[0]["run_id"] if rows else None,
                 "source_errors_latest":sum(x.get("state")!="FETCHED" for x in json.loads((root/rows[0]["run_id"]/"manifest.json").read_text()).get("sources",[])) if rows else 0}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    html,summary=build(a.root,a.out)
    a.out.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    if a.out.parent.stat().st_mode&0o077:
        raise PermissionError("Private destination directory required")
    with a.out.open("xb") as f:
        os.fchmod(f.fileno(),0o600)
        f.write(html.encode("utf-8"))
    print(json.dumps({"file":str(a.out),**summary},indent=2))
if __name__=="__main__":main()
