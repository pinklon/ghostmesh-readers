"""Scout bounded, offline content comparison of retained source snapshots.

Input is local files with known revision identities. The diff reports literal text changes,
not scientific novelty, collaborator interest, or GhostMesh impact.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path

MAX_BYTES = 500_000
MAX_LINES = 350
MAX_DIFF_LINES = 100
MAX_LINE_CHARS = 220

def compare(old: bytes, new: bytes, old_revision: str, new_revision: str, source_url: str) -> dict:
    if not old or not new or len(old) > MAX_BYTES or len(new) > MAX_BYTES:
        raise ValueError("Snapshot length outside bounded comparison")
    if not isinstance(old_revision, str) or not old_revision.strip() or not isinstance(new_revision, str) or not new_revision.strip():
        raise ValueError("Both exact revision identities required")
    if not isinstance(source_url, str) or not source_url.startswith("https://"):
        raise ValueError("Public HTTPS origin required")
    former=old.decode("utf-8",errors="strict").splitlines()
    latter=new.decode("utf-8",errors="strict").splitlines()
    identical=old==new
    hashes={"before":hashlib.sha256(old).hexdigest(),"after":hashlib.sha256(new).hexdigest()}
    if identical and old_revision!=new_revision:
        state="SAME_BYTES_DIFFERENT_REVISION"
    elif identical:
        state="IDENTICAL_BYTES"
    else:
        state="BYTES_CHANGED"
    # Diff is bounded; if source is large, a truncated comparison must not
    # masquerade as an exhaustive inspection.
    bounded_old=[line[:MAX_LINE_CHARS] for line in former[:MAX_LINES]]
    bounded_new=[line[:MAX_LINE_CHARS] for line in latter[:MAX_LINES]]
    diff=list(difflib.unified_diff(bounded_old,bounded_new,fromfile=old_revision,tofile=new_revision,lineterm=""))
    shown=diff[:MAX_DIFF_LINES]
    truncated=(not identical) and (len(former)>MAX_LINES or len(latter)>MAX_LINES or
               any(len(s)>MAX_LINE_CHARS for s in former+ latter) or len(diff)>MAX_DIFF_LINES)
    return {
      "schema":"scout-content-diff-v0","source_url":source_url,
      "before_revision":old_revision,"after_revision":new_revision,
      "before_bytes":len(old),"after_bytes":len(new),"sha256":hashes,
      "observation":state,"bounded_unified_diff":shown,"diff_truncated":truncated,
      "diff_scope":"PREFIX_ONLY" if truncated else "COMPLETE_TEXT",
      "semantic_change":"NOT_EVALUATED","ghostmesh_thesis_impact":"NOT_EVALUATED",
      "editorial_review_required":state!="IDENTICAL_BYTES",
      "notes":["Byte changes alone do not establish a significant scientific or code change",
               "Identical snapshots across distinct versions do not establish repository-wide identity",
               "A truncated diff cannot establish absence of changes outside its inspected section"],
      "publication_authorized":False,"outreach_authorized":False
    }

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--before",type=Path,required=True)
    p.add_argument("--after",type=Path,required=True)
    p.add_argument("--before-revision",required=True)
    p.add_argument("--after-revision",required=True)
    p.add_argument("--source-url",required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists(): raise SystemExit("Refusing overwrite")
    out=compare(a.before.read_bytes(),a.after.read_bytes(),a.before_revision,a.after_revision,a.source_url)
    a.out.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("observation","diff_scope","diff_truncated","semantic_change","ghostmesh_thesis_impact")},indent=2))
if __name__=="__main__":main()
