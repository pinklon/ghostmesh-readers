"""Explicit, one-shot Scout source collection trial with auditable receipts.

No scheduler, outreach, publication, or automatic ranking. Run only in an
authorized network-enabled isolated environment.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from scout_source_collector import collect

DEFAULT_SOURCES = [
    ("debate", "https://arxiv.org/abs/2601.19921"),
    ("sensemaking", "https://arxiv.org/abs/2606.09840"),
    ("negative-control", "https://raw.githubusercontent.com/python/cpython/main/README.rst"),
]

def trial(out: Path, sources=DEFAULT_SOURCES, collector=collect) -> dict:
    if out.exists() and any(out.iterdir()):
        raise ValueError("Output directory must be new or empty; receipts must not overwrite prior runs")
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for label, url in sources:
        if not label.replace("-", "").isalnum() or "/" in label or "\\" in label:
            raise ValueError("Invalid source label")
        snapshots = []
        try:
            packet = collector(url, snapshot_callback=snapshots.append)
            if len(snapshots) != 1:
                raise ValueError("Collector did not return exactly one source snapshot")
            raw = snapshots[0]
            path = out / (label + ".snapshot")
            with path.open("xb") as dest:
                dest.write(raw)
            packet["snapshot_file"] = path.name
            (out / (label + ".json")).write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            results.append({"id": label, "status": "FETCHED_UNVERIFIED",
                            "source_url": url, "snapshot_sha256": packet["snapshot_sha256"],
                            "snapshot_bytes": packet["snapshot_bytes"],
                            "extraction_status": packet["substantive_text"]["extraction_status"]})
        except Exception as exc:
            results.append({"id": label, "source_url": url, "status": "FETCH_FAILED",
                            "error_type": type(exc).__name__})
    manifest = {"schema": "scout-live-trial-v0", "publication_authorized": False,
                "outreach_authorized": False, "independent_evaluation": False,
                "results": results}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = trial(args.out)
    print(json.dumps(result, indent=2))
    if any(item["status"] != "FETCHED_UNVERIFIED" for item in result["results"]):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
