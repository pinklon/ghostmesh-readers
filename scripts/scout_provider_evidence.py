#!/usr/bin/env python3
"""Capture bounded first-party context for Scout comparison candidates.

This is a review aid, not a capability assessment. A changed heading, RSS title,
or successfully fetched page cannot establish feature status or account access.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from scout_provider_diff import (OUTPUT_SCHEMA, SCHEMA as OBSERVATION_SCHEMA,
                                 entry_key, heading_window, validate)
from scout_provider_watch import ensure_url, fetch, validate_registry

SCHEMA = "ghostmesh-scout-provider-evidence-v1"
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_EXCERPT = 2_000
ENTRY_KINDS = {"new-source-entry", "changed-entry-title"}
HEADING_KIND = "source-heading-window-change"


class VisibleText(HTMLParser):
    """Extract bounded readable blocks, never a claim or an availability signal."""

    BLOCKS = {"h1", "h2", "h3", "p", "li"}
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "template", "iframe"}
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = []
        self.active = None
        self.parts = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if self.skip:
            if tag not in self.VOID:
                self.skip.append(tag)
            return
        properties = dict(attrs)
        style = re.sub(r"\s+", "", properties.get("style") or "").lower()
        if (tag in self.SKIP or "hidden" in properties or "inert" in properties
                or (properties.get("aria-hidden") or "").lower() == "true"
                or "display:none" in style or "visibility:hidden" in style):
            self.skip.append(tag)
        elif self.active is None and tag in self.BLOCKS:
            self.active, self.parts = tag, []

    def handle_endtag(self, tag):
        if self.skip:
            if tag in self.skip:
                while self.skip.pop() != tag:
                    pass
            return
        if tag == self.active:
            value = " ".join(" ".join(self.parts).split())
            if value and (not self.blocks or self.blocks[-1] != value):
                self.blocks.append(value)
            self.active, self.parts = None, []

    def handle_data(self, data):
        if self.active is not None and not self.skip:
            self.parts.append(data)


def visible_excerpt(payload, anchors=()):
    parser = VisibleText()
    parser.feed(payload.decode("utf-8", errors="replace"))
    start = 0
    for anchor in anchors:
        if isinstance(anchor, str) and anchor.strip():
            start = next((i for i, block in enumerate(parser.blocks)
                          if anchor.casefold() in block.casefold()), -1)
            if start >= 0:
                break
    if start < 0:
        start = 0
    return "\n".join(parser.blocks[start:])[:MAX_EXCERPT]


def review_targets(candidates, current, registry):
    validate_registry(registry)
    if (not isinstance(candidates, dict) or candidates.get("schema") != OUTPUT_SCHEMA
            or candidates.get("publication_status") != "NOT_APPROVED"
            or not isinstance(candidates.get("candidates"), list)
            or not isinstance(current, dict) or current.get("schema") != OBSERVATION_SCHEMA
            or candidates.get("current_observed_at") != current.get("observed_at")):
        raise ValueError("Comparison and observation identity mismatch")
    observations = validate(current)
    sources = {item["id"]: item for item in registry["sources"]}
    if set(observations) != set(sources):
        raise ValueError("Observation omits a registered source")
    health = candidates.get("source_health")
    if (not isinstance(health, list) or len(health) != len(sources)
            or {item.get("id") for item in health if isinstance(item, dict)} != set(sources)):
        raise ValueError("Incomplete source health matrix")
    targets, seen = [], set()
    for candidate in candidates["candidates"]:
        if not isinstance(candidate, dict) or candidate.get("kind") not in ENTRY_KINDS | {HEADING_KIND}:
            raise ValueError("Unsupported comparison candidate")
        ident, source_id = candidate.get("id"), candidate.get("source_id")
        source, observation = sources.get(source_id), observations.get(source_id)
        if (not isinstance(ident, str) or not ident or ident in seen or not source or not observation
                or observation.get("status") != "observed"
                or observation.get("source_url") != source["url"]
                or observation.get("provider") != source["provider"]
                or not SHA.fullmatch(str(observation.get("sha256", "")))
                or candidate.get("provider") != source["provider"]
                or candidate.get("editorial_status") != "NOT_APPROVED"):
            raise ValueError("Candidate lacks an attributable official observation")
        seen.add(ident)
        if candidate["kind"] == HEADING_KIND:
            if (source["format"] != "html" or candidate.get("source_url") != source["url"]):
                raise ValueError("Heading change is not bound to its official page")
            headings = heading_window(observation)
            expected = (sha256((source_id + "\n" + source["url"] + "\n" +
                        json.dumps(headings, ensure_ascii=False)).encode("utf-8")).hexdigest()[:24]
                        if headings is not None else None)
            if ident != expected:
                raise ValueError("Heading candidate identity differs from observed headings")
            added = candidate.get("added_headings")
            if (not isinstance(added, list) or not all(isinstance(x, str) and
                    x in [heading[1] for heading in headings] for x in added)):
                raise ValueError("Heading excerpt anchors differ from observed headings")
            target_url = source["url"]
            source_scope = "page-heading-change-only"
        else:
            if source["format"] != "rss":
                raise ValueError("Entry candidate is not from an official feed")
            target_url = ensure_url(candidate.get("url"))
            if urlsplit(target_url).hostname != urlsplit(source["url"]).hostname:
                raise ValueError("Feed entry left its first-party source host")
            matches = [entry for entry in observation.get("entries", [])
                       if isinstance(entry, dict) and entry_key(source_id, entry) == ident]
            if len(matches) != 1 or matches[0].get("title") != candidate.get("title"):
                raise ValueError("Entry candidate does not match the observed feed")
            source_scope = "feed-entry-metadata-only"
        targets.append({"candidateId": ident, "sourceId": source_id,
                        "provider": source["provider"], "changeKind": candidate["kind"],
                        "officialFeedOrPageUrl": source["url"], "officialEvidenceUrl": target_url,
                        "observedSourceSha256": observation["sha256"],
                        "sourceScope": source_scope,
                        "excerptAnchors": added if candidate["kind"] == HEADING_KIND else [candidate["title"]]})
    return targets


def fetch_context(source):
    return fetch(source, include_final_url=True)


def same_document(expected, actual):
    a, b = urlsplit(expected), urlsplit(ensure_url(actual))
    return (a.scheme, a.hostname, a.path.rstrip("/"), a.query) == (b.scheme, b.hostname, b.path.rstrip("/"), b.query)


def capture(candidates, current, registry, now=None, fetch_page=fetch_context):
    targets = review_targets(candidates, current, registry)
    captured_at = now or datetime.now(timezone.utc).isoformat()
    records, cache = [], {}
    for target in targets:
        url = target["officialEvidenceUrl"]
        if url not in cache:
            try:
                payload, final_url = fetch_page({"url": url})
                cache[url] = {"captureSha256": sha256(payload).hexdigest(), "payload": payload,
                              "redirectStatus": "same-document" if same_document(url, final_url)
                              else "DIFFERENT_SOURCE"}
            except Exception as exc:
                cache[url] = {"captureStatus": "UNKNOWN", "errorType": type(exc).__name__,
                              "visibleExcerpt": ""}
        cached = cache[url]
        record = dict(target)
        if "payload" in cached:
            excerpt = visible_excerpt(cached["payload"], target["excerptAnchors"])
            record.update(captureStatus="captured" if excerpt else "UNKNOWN",
                          captureSha256=cached["captureSha256"], visibleExcerpt=excerpt,
                          redirectStatus=cached["redirectStatus"])
            if record["redirectStatus"] == "DIFFERENT_SOURCE":
                record["captureStatus"] = "UNKNOWN"
                record["visibleExcerpt"] = ""
        else:
            record.update(cached)
        if (target["sourceScope"] == "page-heading-change-only"
                and record["captureStatus"] == "captured"
                and record["captureSha256"] != target["observedSourceSha256"]):
            record["captureStatus"] = "STALE_SOURCE"
        record.update(capabilityIdentity=None, eventStatus="UNKNOWN",
                      generalAvailability="UNKNOWN", planEntitlement="UNKNOWN",
                      accountEntitlement="UNKNOWN", editorialStatus="NOT_APPROVED")
        records.append(record)
    return {"schema": SCHEMA, "observedAt": current["observed_at"],
            "capturedAt": captured_at, "publicationStatus": "NOT_APPROVED",
            "sourceHealth": candidates["source_health"], "records": records}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = capture(json.loads(args.candidates.read_text()),
                     json.loads(args.observations.read_text()),
                     json.loads(args.registry.read_text()))
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"Scout captured {len(result['records'])} review-only candidates; none assessed or published.")


if __name__ == "__main__":
    main()
