#!/usr/bin/env python3
"""Deterministic, offline diff of two Scout public-source observation snapshots.

Produces review-only candidates. It never asserts a capability launch or publishes.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

SCHEMA = "ghostmesh-scout-provider-observations-v1"
OUTPUT_SCHEMA = "ghostmesh-scout-provider-candidates-v1"
GOOD = {"observed"}


def entry_key(source_id, entry):
    url = entry.get("url", "").strip()
    if not url or urlsplit(url).scheme not in {"http", "https"}:
        return None
    parsed = urlsplit(url)
    normalized = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(),
                             parsed.path.rstrip("/") or "/", parsed.query, ""))
    return sha256((source_id + "\n" + normalized).encode("utf-8")).hexdigest()[:24]


def index_entries(observation):
    """Return None when an observed source has no comparable entry identity."""
    entries = {}
    records = observation.get("entries")
    if not isinstance(records, list) or not records:
        return None
    for entry in records:
        if (not isinstance(entry, dict) or not isinstance(entry.get("title"), str)
                or not entry["title"].strip() or not isinstance(entry.get("url"), str)):
            return None
        key = entry_key(observation["id"], entry)
        if key is None:
            return None
        if key not in entries:
            entries[key] = entry
    return entries


def validate(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("schema") != SCHEMA:
        raise ValueError("Unsupported observation snapshot")
    sources = snapshot.get("observations")
    if not isinstance(sources, list):
        raise ValueError("Missing observation records")
    ids = [source.get("id") for source in sources if isinstance(source, dict)]
    if len(ids) != len(sources) or len(set(ids)) != len(ids) or not all(isinstance(x, str) for x in ids):
        raise ValueError("Invalid or duplicate source IDs")
    return {source["id"]: source for source in sources}


def compare(previous, current):
    before = validate(previous)
    after = validate(current)
    candidates, source_health = [], []
    for source_id in sorted(set(before) | set(after)):
        old, new = before.get(source_id), after.get(source_id)
        if not old or not new or old.get("status") not in GOOD or new.get("status") not in GOOD:
            source_health.append({"id": source_id, "status": "UNKNOWN",
                                  "previous_status": old.get("status") if old else "missing",
                                  "current_status": new.get("status") if new else "missing"})
            continue
        old_entries, new_entries = index_entries(old), index_entries(new)
        if old_entries is None or new_entries is None:
            source_health.append({"id": source_id, "status": "UNKNOWN",
                                  "previous_status": old["status"],
                                  "current_status": new["status"],
                                  "reason": "unsupported-or-empty-entry-shape"})
            continue
        source_health.append({"id": source_id, "status": "comparable"})
        for key in sorted(new_entries.keys() - old_entries.keys()):
            entry = new_entries[key]
            candidates.append({"id": key, "source_id": source_id,
                               "provider": new.get("provider", ""),
                               "kind": "new-source-entry", "title": entry["title"],
                               "url": entry["url"], "published": entry.get("published", ""),
                               "evidence_class": "unreviewed-provider-observation",
                               "editorial_status": "NOT_APPROVED"})
        for key in sorted(new_entries.keys() & old_entries.keys()):
            if new_entries[key].get("title") != old_entries[key].get("title"):
                entry = new_entries[key]
                candidates.append({"id": key, "source_id": source_id,
                                   "provider": new.get("provider", ""),
                                   "kind": "changed-entry-title", "title": entry["title"],
                                   "url": entry["url"], "previous_title": old_entries[key].get("title", ""),
                                   "evidence_class": "unreviewed-provider-observation",
                                   "editorial_status": "NOT_APPROVED"})
    return {"schema": OUTPUT_SCHEMA, "previous_observed_at": previous.get("observed_at"),
            "current_observed_at": current.get("observed_at"),
            "publication_status": "NOT_APPROVED",
            "source_health": source_health, "candidates": candidates}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(json.loads(args.previous.read_text(encoding="utf-8")),
                     json.loads(args.current.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Review-only candidates: {len(result['candidates'])}; no content published.")


if __name__ == "__main__":
    main()
