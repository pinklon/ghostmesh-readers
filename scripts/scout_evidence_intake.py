"""Scout offline candidate evidence intake. Research-only; never fetches URLs or contacts authors."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 200_000
FIELDS = ("contribution", "ghostmesh_gap", "counterargument", "joint_experiment")

def build_packet(url: str, source: bytes, claims: dict | None = None) -> dict:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("A public HTTPS source URL without credentials is required")
    if not source or len(source) > MAX_BYTES:
        raise ValueError("Source snapshot must contain 1 to 200000 bytes")
    text = source.decode("utf-8", errors="strict")
    if not text.strip():
        raise ValueError("Empty text snapshot")
    claims = claims or {}
    if not isinstance(claims, dict) or any(k not in FIELDS for k in claims):
        raise ValueError("Unexpected claim fields")
    if any(not isinstance(v, str) or not v.strip() for v in claims.values()):
        raise ValueError("Claims must be nonempty strings")
    return {
        "schema": "scout-evidence-intake-v0",
        "source_url": url,
        "snapshot_sha256": hashlib.sha256(source).hexdigest(),
        "snapshot_bytes": len(source),
        "source_excerpt": text[:1200],
        "source_capture": "operator-provided local text; source URL not independently fetched",
        "claims": {k: {"value": claims.get(k), "status": "OPERATOR_DRAFT" if k in claims else "UNKNOWN"}
                   for k in FIELDS},
        "evidence_verified": False,
        "review_required": True,
        "outreach_authorized": False,
        "publication_authorized": False,
        "recommendation": "UNASSESSED",
        "limitations": ["Snapshot provenance and author claims require independent verification",
                        "No automatic semantic inference, ranking, or collaboration decision"]
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--claims", type=Path, help="Optional human-authored JSON claims")
    args = parser.parse_args()
    source = args.snapshot.read_bytes()
    claims = json.loads(args.claims.read_text(encoding="utf-8")) if args.claims else None
    print(json.dumps(build_packet(args.url, source, claims), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
