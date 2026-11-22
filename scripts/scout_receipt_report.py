"""Render an owner-private Scout review from actual collector receipts, offline."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def report(receipts: Path) -> str:
    manifest = json.loads((receipts / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "scout-live-trial-v0":
        raise ValueError("Unexpected manifest schema")
    if manifest.get("publication_authorized") is not False or manifest.get("outreach_authorized") is not False:
        raise ValueError("Manifest cannot authorize publication or outreach")
    lines = ["# Scout | Private evidence review", "",
             "> Collector receipts only. Hash verification proves these bytes match the receipt,",
             "> not that author claims are correct or a collaboration is warranted.", "",
             "Publication: **not authorized**. Outreach: **not authorized**.", ""]
    for item in manifest["results"]:
        identity = item["id"]
        if not isinstance(identity, str) or not identity.replace("-", "").isalnum():
            raise ValueError("Unsafe receipt id")
        lines.extend([f"## {identity}", "", f"Source: {item['source_url']}", ""])
        if item["status"] != "FETCHED_UNVERIFIED":
            lines.extend(["**Collection:** FAILED", ""])
            continue
        packet = json.loads((receipts / (identity + ".json")).read_text(encoding="utf-8"))
        raw = (receipts / (identity + ".snapshot")).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if (digest != item["snapshot_sha256"] or digest != packet["snapshot_sha256"]
                or len(raw) != item["snapshot_bytes"] or len(raw) != packet["snapshot_bytes"]
                or item["source_url"] != packet["source_url"]):
            raise ValueError(f"Receipt mismatch for {identity}")
        extraction = packet["substantive_text"]
        lines.extend([f"Snapshot SHA-256: `{digest}`",
                      f"Captured bytes: {len(raw)}",
                      f"Text extraction: **{extraction['extraction_status']}**",
                      f"Title: {extraction.get('title') or '(not supplied)'}", "",
                      "**Source excerpt (unverified author/source material):**", "",
                      "> " + (extraction.get("excerpt") or "(none)").replace("\n", "\n> ")[:1000],
                      "", "**Editorial interpretation:** NOT ASSESSED IN THIS RECEIPT.",
                      "**Counterargument / experiment:** Requires separate human review.", ""])
    lines.extend(["## Review boundaries", "",
                  "No comparison scores, semantic accuracy, independent replication, or collaborator intent are established.",
                  "A valid snapshot is not evidence that any recommended integration works.", ""])
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing to overwrite report")
    args.out.write_text(report(args.receipts), encoding="utf-8")
    print(str(args.out))

if __name__ == "__main__":
    main()
