#!/usr/bin/env python3
"""Observe first-party public release sources. No publication or repository mutation."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "content/scout/provider-sources.json"
MAX_BYTES = 1_000_000
MAX_ENTRIES = 12
ALLOWED_HOSTS = {
    "openai.com", "platform.claude.com", "support.claude.com",
    "ai.google.dev", "learn.microsoft.com", "github.blog",
}
ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def validate_registry(data):
    if set(data) != {"schema", "sources"} or data["schema"] != "ghostmesh-scout-provider-sources-v1":
        raise ValueError("Source registry schema")
    if not isinstance(data["sources"], list) or not data["sources"]:
        raise ValueError("Source registry empty")
    seen = set()
    for entry in data["sources"]:
        if not isinstance(entry, dict) or set(entry) != {"id", "provider", "format", "url"}:
            raise ValueError("Source fields")
        if not isinstance(entry["id"], str) or not ID_RE.fullmatch(entry["id"]) or entry["id"] in seen:
            raise ValueError("Duplicate or invalid source ID")
        seen.add(entry["id"])
        if not isinstance(entry["provider"], str) or not entry["provider"].strip():
            raise ValueError("Provider name")
        if entry["format"] not in {"rss", "html"}:
            raise ValueError("Unsupported format")
        ensure_url(entry["url"])
    return data


def ensure_url(url):
    if not isinstance(url, str):
        raise ValueError("Non-string URL")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password or parsed.port:
        raise ValueError("Source URL outside approved first-party hosts")
    return url


def fetch(source):
    request = Request(source["url"], headers={"User-Agent": "GhostMeshScoutPublicReleaseWatch/1.0", "Accept": "application/rss+xml, application/atom+xml, text/html, application/xml"})
    with urlopen(request, timeout=12) as response:
        ensure_url(response.geturl())
        payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise ValueError("Source exceeds bounded response size")
    return payload


def element_text(node, names):
    for name in names:
        child = node.find(name)
        if child is not None and child.text and child.text.strip():
            return child.text.strip()
    return ""


def parse_feed(payload):
    root = ET.fromstring(payload)
    entries = []
    if root.tag.endswith("rss"):
        nodes = root.findall("./channel/item")
        for node in nodes[:MAX_ENTRIES]:
            entries.append({"title": element_text(node, ["title"])[:240],
                            "url": element_text(node, ["link"])[:500],
                            "published": element_text(node, ["pubDate"])[:100]})
    elif root.tag.endswith("feed"):
        ns = "{http://www.w3.org/2005/Atom}"
        for node in root.findall(ns + "entry")[:MAX_ENTRIES]:
            link = node.find(ns + "link")
            entries.append({"title": element_text(node, [ns + "title"])[:240],
                            "url": link.attrib.get("href", "")[:500] if link is not None else "",
                            "published": element_text(node, [ns + "published", ns + "updated"])[:100]})
    else:
        raise ValueError("Not RSS or Atom")
    return [entry for entry in entries if entry["title"] and entry["url"]]


class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.heading = None
        self.parts = []
        self.headings = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.depth += 1
        if not self.depth and tag in {"h1", "h2", "h3"}:
            self.heading = tag
            self.parts = []

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.depth:
            self.depth -= 1
        if tag == self.heading:
            value = " ".join(" ".join(self.parts).split())
            if value:
                self.headings.append({"level": tag, "text": value[:240]})
            self.heading = None
            self.parts = []

    def handle_data(self, data):
        if self.heading is not None and not self.depth:
            self.parts.append(data)


def parse_html(payload):
    parser = HeadingParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    return parser.headings[:MAX_ENTRIES]


def observe(source, now):
    record = {"id": source["id"], "provider": source["provider"],
              "source_url": source["url"], "observed_at": now, "status": "unknown",
              "evidence_class": "unreviewed-provider-observation"}
    try:
        payload = fetch(source)
        entries = parse_feed(payload) if source["format"] == "rss" else parse_html(payload)
        record.update(status="observed", sha256=sha256(payload).hexdigest(), entries=entries)
        if not entries:
            record["status"] = "unparsed"
    except Exception as exc:
        # Do not turn fetch failures into zero releases. Do not expose request internals.
        record.update(status="unknown", error_type=type(exc).__name__)
    return record


def collect(registry, now=None):
    validate_registry(registry)
    now = now or datetime.now(timezone.utc).isoformat()
    observations = [observe(source, now) for source in registry["sources"]]
    return {"schema": "ghostmesh-scout-provider-observations-v1", "observed_at": now,
            "publication_status": "NOT_APPROVED", "source_count": len(observations),
            "observations": observations}


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--registry", type=Path, default=REGISTRY)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    result = collect(json.loads(args.registry.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Scout observed {result['source_count']} first-party sources. No content published.")


if __name__ == "__main__":
    main()
