"""Scout private-run archive and restore qualification. No pruning or scheduling.

Copies an immutable run into a private destination, verifies source manifest and
copied hashes, and produces a retention inventory. Never deletes source runs.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, stat, tempfile
from pathlib import Path

def _private(path):
    if path.is_symlink() or (stat.S_IMODE(path.stat().st_mode)&0o077):
        raise PermissionError("Private non-symlink directory required")

def verify_run(run):
    run=Path(run);_private(run)
    manifest=json.loads((run/"manifest.json").read_text())
    if manifest.get("schema")!="scout-integrated-run-v0" or manifest.get("publication_authorized") is not False or manifest.get("outreach_authorized") is not False:
        raise ValueError("Invalid private Scout run")
    digests=manifest.get("sha256")
    if not isinstance(digests,dict) or not digests:raise ValueError("Missing integrity manifest")
    expected=set(digests)|{"manifest.json"}
    actual={f.name for f in run.iterdir()}
    if actual!=expected:raise ValueError("Unexpected or missing run files")
    for name,digest in digests.items():
        if Path(name).name!=name or not isinstance(digest,str) or len(digest)!=64:raise ValueError("Invalid receipt name or hash")
        f=run/name
        if f.is_symlink() or not f.is_file():raise ValueError("Untrusted source file")
        if hashlib.sha256(f.read_bytes()).hexdigest()!=digest:raise ValueError("Hash mismatch: "+name)
    return manifest

def copy_verified(run,destination):
    run=Path(run); destination=Path(destination)
    manifest=verify_run(run)
    if destination.exists():raise FileExistsError("Refusing backup overwrite")
    destination.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    _private(destination.parent)
    stage=Path(tempfile.mkdtemp(prefix=".scout-backup-",dir=destination.parent))
    try:
        for item in run.iterdir():
            shutil.copyfile(item,stage/item.name)
            os.chmod(stage/item.name,0o600)
        verify_run(stage)
        os.rename(stage,destination)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return {"run_id":manifest["run_id"],"backup":str(destination),
            "files":len(manifest["sha256"])+1,"sha256_verified":True,
            "source_preserved":True,"automatic_deletion":False}

def inventory(root):
    root=Path(root);_private(root)
    rows=[]
    for p in sorted(root.iterdir()):
        if p.name.startswith("."):continue
        if p.is_symlink() or not p.is_dir():raise ValueError("Unexpected root entry")
        try:
            m=verify_run(p)
            rows.append({"run_id":m["run_id"],"captured_utc":m.get("captured_utc"),
                         "sources":len(m.get("sources",[])),"leads":m.get("leads"),
                         "integrity":"VERIFIED","retention":"KEEP_UNTIL_OWNER_POLICY"})
        except Exception as exc:
            rows.append({"run_id":p.name,"integrity":"NEEDS_REVIEW",
                         "error_type":type(exc).__name__,"retention":"HOLD_NO_DELETE"})
    return {"schema":"scout-private-retention-inventory-v0","runs":rows,
            "deleted":0,"automatic_pruning":False,
            "note":"Listing and verification only; backups to another folder on this host do not protect against host loss"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="action",required=True)
    a=sub.add_parser("backup");a.add_argument("--run",required=True,type=Path);a.add_argument("--dest",required=True,type=Path)
    a=sub.add_parser("inventory");a.add_argument("--root",required=True,type=Path)
    args=p.parse_args()
    result=copy_verified(args.run,args.dest) if args.action=="backup" else inventory(args.root)
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
