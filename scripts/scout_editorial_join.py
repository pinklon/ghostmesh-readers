"""Join verified Scout receipts with separately authored, explicitly unreviewed editorial drafts."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from scout_receipt_report import report

ALLOWED = {"ARCHIVE", "FOLLOW", "INVESTIGATE", "CONSIDER_INTRODUCTION", "NO_CONNECTION_JUSTIFIED"}

def join(receipts: Path, assessment_file: Path) -> str:
    # Recompute all snapshot hashes and verify metadata before trusting editorial bindings.
    evidence = report(receipts)
    manifest = json.loads((receipts / "manifest.json").read_text(encoding="utf-8"))
    assessments = json.loads(assessment_file.read_text(encoding="utf-8"))
    if (assessments.get("schema") != "scout-editorial-assessments-v0"
            or assessments.get("review_state") != "AUTHOR_DRAFT_NOT_INDEPENDENTLY_REVIEWED"
            or assessments.get("outreach_authorized") is not False
            or assessments.get("publication_authorized") is not False):
        raise ValueError("Editorial file has an invalid review or authorization state")
    source_index = {r["id"]: r for r in manifest["results"]}
    items = assessments.get("cases")
    if not isinstance(items, list) or len(items) != len(source_index):
        raise ValueError("Editorial assessment coverage does not match receipts")
    seen = set()
    sections = []
    for item in items:
        identity = item.get("id")
        if identity in seen or identity not in source_index:
            raise ValueError("Duplicate or unknown editorial source")
        seen.add(identity)
        source = source_index[identity]
        if source["status"] != "FETCHED_UNVERIFIED" or item.get("snapshot_sha256") != source["snapshot_sha256"]:
            raise ValueError("Editorial source hash mismatch or unsuccessful collection")
        if item.get("recommendation") not in ALLOWED:
            raise ValueError("Invalid editorial recommendation")
        for field in ("contribution", "ghostmesh_gap", "counterargument", "joint_experiment"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError("Missing editorial field: " + field)
        sections.extend([
            "## " + identity, "",
            "**Provenance:** matched to a verified collected snapshot SHA-256 `" + item["snapshot_sha256"] + "`.",
            "**Assessment status:** AUTHOR DRAFT, NOT INDEPENDENTLY REVIEWED.", "",
            "**Contribution interpretation:** " + item["contribution"], "",
            "**GhostMesh gap:** " + item["ghostmesh_gap"], "",
            "**Strongest counterargument:** " + item["counterargument"], "",
            "**Proposed experiment:** " + item["joint_experiment"], "",
            "**Editorial recommendation:** " + item["recommendation"], "",
        ])
    return ("# Scout | Evidence-linked editorial research draft\n\n"
            "> This is source-hash-bound editorial interpretation, not validated scientific findings.\n"
            "> Neither publication nor outreach is authorized.\n\n"
            + "\n".join(sections)
            + "\n## Collector evidence appendix\n\n" + evidence)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--assessments", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing to overwrite existing editorial report")
    content = join(args.receipts, args.assessments)
    args.out.write_text(content, encoding="utf-8")
    print(str(args.out))

if __name__ == "__main__":
    main()
