"""Move public delivery URLs without reopening source-qualified Readers.

Only the staged deployment is transformed. Historical GUIDs, schema identities,
source files and release receipts stay unchanged. Derived knowledge hashes are
rebound only after an exact old-byte witness and a host-only HTML projection.
"""
from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

OLD = "https://youtube.shareplane.malott.ai"
NEW = "https://readers.ghostmesh.ai"
OLD_HOST = urlsplit(OLD).hostname
NEW_HOST = urlsplit(NEW).hostname
RECEIPT = ".well-known/ghostmesh-origin-migration.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value, compact=False):
    if compact:
        return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")) + "\n").encode()
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def new_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.netloc != OLD_HOST
            or parsed.username or parsed.password):
        raise ValueError(f"Not an exact legacy Reader URL: {value}")
    return NEW + value[len(OLD):]


class OriginAttributes(HTMLParser):
    """Prove every legacy occurrence is an approved HTML transport attribute."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.count = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for key, value in attrs:
            if not value or OLD_HOST not in value:
                continue
            allowed = ((tag == "a" and key == "href")
                       or (tag == "link" and key == "href" and values.get("rel") == "canonical")
                       or (tag == "meta" and key == "content"
                           and (values.get("property") or values.get("name"))
                           in {"og:url", "og:image", "twitter:image"}))
            if not allowed or value.count(OLD_HOST) != 1:
                raise ValueError("Legacy hostname occurs outside approved URL attributes")
            new_url(value)
            self.count += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def project_html(raw):
    text = raw.decode("utf-8")
    parsed = OriginAttributes()
    parsed.feed(text)
    parsed.close()
    if parsed.count != text.count(OLD_HOST):
        raise ValueError("Legacy hostname occurs in HTML text or unsupported markup")
    result = text.replace(OLD, NEW).encode()
    if result.count(NEW.encode()) - raw.count(NEW.encode()) != parsed.count:
        raise ValueError("HTML origin projection count mismatch")
    return result


def project(root: Path):
    """Project an isolated, fully-built public directory to its new origin."""
    root = root.resolve()
    changes = {}
    def read(rel):
        return (root / rel).read_bytes()
    def write(rel, value):
        before = read(rel)
        if before != value:
            changes[rel] = {"path": rel, "sourceSha256": digest(before),
                            "projectedSha256": digest(value)}
            (root / rel).write_bytes(value)
    def load(rel):
        return json.loads(read(rel))
    def put(rel, obj, compact=False):
        write(rel, encoded(obj, compact))

    # HTML presentation only. No article text or reviewed source file changes.
    for path in sorted(root.rglob("*.html")):
        rel = path.relative_to(root).as_posix()
        raw = read(rel)
        if OLD_HOST.encode() in raw:
            write(rel, project_html(raw))

    catalog = load("catalog.json")
    if catalog["host"] != OLD:
        raise ValueError("Unexpected original Reader catalog authority")
    catalog["host"] = NEW
    put("catalog.json", catalog)

    # Search corpus matches and all editorial fields remain unchanged.
    path = "readers/unified-search-index.json"
    index = load(path)
    reader_records = [row for row in index["records"] if row["source"] == "Readers"]
    expected = {row["id"]: "/" + row["slug"] + "/" for row in catalog["readers"]}
    if {row["id"]: urlsplit(row["url"]).path for row in reader_records} != expected:
        raise ValueError("Unified Reader identity mismatch before hostname projection")
    for row in reader_records:
        row["url"] = new_url(row["url"])
    put(path, index)
    path = "assets/reader-search.js"
    raw = read(path)
    if raw.count(OLD_HOST.encode()) != 2:
        raise ValueError("Search origin validation changed; review projection")
    write(path, raw.replace(OLD_HOST.encode(), NEW_HOST.encode()))

    path = "map/relationships.json"
    model = load(path)
    for node in model["nodes"]:
        node["url"] = new_url(node["url"])
    put(path, model)
    path = "scout/research/relationships.json"
    model = load(path)
    for node in model["nodes"]:
        node["url"] = new_url(node["url"])
    for edge in model["edges"]:
        for key in ("fromUrl", "toUrl"):
            edge[key] = new_url(edge[key])
    put(path, model)

    # Only location elements, never release GUIDs or editorial descriptions.
    for rel, tag in (("feed.xml", "link"), ("sitemap.xml", "loc")):
        raw = read(rel)
        prefix = f"<{tag}>{OLD}".encode()
        if raw.count(prefix) != raw.count(OLD_HOST.encode()):
            raise ValueError(f"Legacy hostname outside location elements: {rel}")
        write(rel, raw.replace(prefix, f"<{tag}>{NEW}".encode()))
    for rel in ("robots.txt", "llms.txt"):
        write(rel, read(rel).replace(OLD.encode(), NEW.encode()))

    # A reviewed page remains source authority; the derived graph must bind to
    # the bytes actually delivered by this projection. Rebind only witnessed
    # old page hashes, retaining exact claims, anchors, quote hashes and IDs.
    path = "knowledge/v0.1/readers.json"
    graph = load(path)
    witnesses = {}
    for node in graph["nodes"]:
        if node["type"] != "Reader":
            continue
        rel = node["source"]["path"].removeprefix("site/")
        change = changes.get(rel)
        if not change or node["source"]["sha256"] != change["sourceSha256"]:
            raise ValueError(f"Reader page hash not witnessed: {rel}")
        node["url"] = new_url(node["url"])
        node["source"]["sha256"] = change["projectedSha256"]
        witnesses[node["id"]] = change

    def rebind(provenance):
        witness = witnesses[provenance["sourceNodeId"]]
        if provenance["sourceFileSha256"] != witness["sourceSha256"]:
            raise ValueError("Citation does not bind original source bytes")
        provenance["sourceFileSha256"] = witness["projectedSha256"]

    for node in graph["nodes"]:
        if node["type"] == "Claim":
            rebind(node["provenance"])
    for edge in graph["relationships"]:
        rebind(edge["provenance"])
    put(path, graph, True)

    path = "knowledge/v0.1/readers.jsonld"
    ld = load(path)
    for node in ld["@graph"]:
        if node["@id"] in witnesses:
            node["schema:url"] = new_url(node["schema:url"])
        if "gm:provenance" in node:
            rebind(node["gm:provenance"])
    # @context terms are semantic identities, not delivery URLs.
    put(path, ld, True)
    path = "knowledge/v0.1/claim-register.json"
    register = load(path)
    for claim in register["claims"]:
        witness = witnesses["urn:ghostmesh-readers:reader:" + claim["readerSlug"]]
        if claim["readerSha256"] != witness["sourceSha256"]:
            raise ValueError("Claim register original page hash mismatch")
        claim["readerSha256"] = witness["projectedSha256"]
        claim["claimUrl"] = new_url(claim["claimUrl"])
    put(path, register, True)

    path = ".well-known/ghostmesh-knowledge.json"
    discovery = load(path)
    for key in ("human", "json", "jsonld", "schema", "manifest", "scoutResearchRelationships"):
        discovery[key] = new_url(discovery[key])
    put(path, discovery, True)

    # Keep the original source/schema hashes; attest the newly rendered output
    # bytes using the existing manifest algorithm.
    path = "knowledge/v0.1/publication-manifest.json"
    manifest = load(path)
    for output in manifest["outputs"]:
        rel = output["path"].removeprefix("site/")
        payload = read(rel)
        change = changes.get(rel)
        before_sha = change["sourceSha256"] if change else digest(payload)
        if output["sha256"] != before_sha:
            raise ValueError(f"Knowledge manifest did not bind original output: {rel}")
        output["sha256"], output["bytes"] = digest(payload), len(payload)
    manifest["outputsDigest"] = digest(encoded(manifest["outputs"], True))
    put(path, manifest, True)

    # No unclassified legacy delivery links. Only stable schema/vocab identity
    # may retain the old origin; historical release source records are not copied.
    allowed_legacy = {"knowledge/v0.1/contract.schema.json": OLD + "/knowledge/v0.1/contract.schema.json",
                      "knowledge/v0.1/readers.jsonld": OLD + "/knowledge/v0.1/vocab#"}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".html", ".json", ".jsonld", ".xml", ".txt", ".js", ".webmanifest"}:
            rel = path.relative_to(root).as_posix()
            raw = path.read_bytes()
            if rel in allowed_legacy:
                raw = raw.replace(allowed_legacy[rel].encode(), b"", 1)
            if OLD_HOST.encode() in raw:
                raise ValueError(f"Unclassified legacy hostname: {rel}")
    receipt = {"schema": "ghostmesh-public-origin-projection-v1",
               "originalOrigin": OLD, "canonicalOrigin": NEW,
               "scope": "delivery URLs and derived published-page digest bindings only",
               "files": [changes[key] for key in sorted(changes)]}
    (root / RECEIPT).write_bytes(encoded(receipt))
    return receipt
