#!/usr/bin/env python3
"""Deterministic, offline diff of two Scout public-source observation snapshots.

Produces review-only candidates. It never asserts a capability launch or publishes.
"""
import argparse
from collections import Counter
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


def heading_window(observation):
    """Validate a bounded HTML heading window; it has no feature identity."""
    records = observation.get("entries")
    if not isinstance(records, list) or not records:
        return None
    headings = []
    for entry in records:
        if (not isinstance(entry, dict) or entry.get("level") not in {"h1", "h2", "h3"}
                or not isinstance(entry.get("text"), str) or not entry["text"].strip()):
            return None
        headings.append((entry["level"], entry["text"].strip()))
    return headings


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
        old_headings, new_headings = heading_window(old), heading_window(new)
        if old_headings is not None or new_headings is not None:
            source_url = new.get("source_url")
            if (old_headings is None or new_headings is None
                    or old.get("source_url") != source_url
                    or not isinstance(source_url, str)
                    or urlsplit(source_url).scheme != "https"):
                source_health.append({"id": source_id, "status": "UNKNOWN",
                                      "reason": "unsupported-or-changed-heading-source"})
                continue
            source_health.append({"id": source_id, "status": "heading-only",
                                  "reason": "no-feature-identity"})
            if old_headings != new_headings:
                old_counts, new_counts = Counter(old_headings), Counter(new_headings)
                key = sha256((source_id + "\n" + source_url + "\n" +
                              json.dumps(new_headings, ensure_ascii=False)).encode("utf-8")).hexdigest()[:24]
                candidates.append({"id": key, "source_id": source_id,
                                   "provider": new.get("provider", ""),
                                   "kind": "source-heading-window-change",
                                   "source_url": source_url,
                                   "added_headings": [text for (_, text) in (new_counts - old_counts).elements()],
                                   "removed_headings": [text for (_, text) in (old_counts - new_counts).elements()],
                                   "evidence_class": "unreviewed-provider-observation",
                                   "editorial_status": "NOT_APPROVED"})
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


def unknown_baseline(current):
    """A first snapshot cannot establish that any observed entry is new."""
    sources = validate(current)
    return {"schema": OUTPUT_SCHEMA, "previous_observed_at": None,
            "current_observed_at": current.get("observed_at"),
            "publication_status": "NOT_APPROVED",
            "source_health": [{"id": source_id, "status": "UNKNOWN",
                               "reason": "no-prior-scheduled-snapshot"}
                              for source_id in sorted(sources)],
            "candidates": []}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    current = json.loads(args.current.read_text(encoding="utf-8"))
    result = (compare(json.loads(args.previous.read_text(encoding="utf-8")), current)
              if args.previous else unknown_baseline(current))
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Review-only candidates: {len(result['candidates'])}; no content published.")


if __name__ == "__main__":
    main()
