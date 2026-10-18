#!/usr/bin/env python3
"""Offline, source-only public projection. Uses only the Python standard library."""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "knowledge/v0.1/readers.source.json"
SCHEMA = ROOT / "knowledge/v0.1/contract.schema.json"
HOST = "https://youtube.shareplane.malott.ai"
DENIED = (
    re.compile(r"/Users/|/private/|/srv/|80-private/|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY", re.I),
    re.compile(r"\b(?:ghp_|gho_|sk-)[A-Za-z0-9_-]{12,}"),
    re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|(?:AKIA|ASIA)[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{30,}|xox[baprs]-[A-Za-z0-9-]{12,})"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def validate_schema(value: object, rule: dict, schema: dict, at: str = "$") -> None:
    """Evaluate the closed JSON Schema vocabulary used by contract.schema.json."""
    if "$ref" in rule:
        ref = rule["$ref"]
        if not ref.startswith("#/$defs/"):
            raise ValueError(f"{at}: unsupported schema reference")
        validate_schema(value, schema["$defs"][ref.split("/")[-1]], schema, at)
        return
    if "oneOf" in rule:
        if isinstance(value, dict):
            for choice in rule["oneOf"]:
                ref = choice.get("$ref", "")
                if ref.startswith("#/$defs/"):
                    candidate = schema["$defs"][ref.split("/")[-1]]
                    if candidate.get("properties", {}).get("type", {}).get("const") == value.get("type"):
                        validate_schema(value, choice, schema, at)
                        return
        matches = 0
        for choice in rule["oneOf"]:
            try:
                validate_schema(value, choice, schema, at)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            raise ValueError(f"{at}: expected exactly one node shape")
        return
    if "const" in rule and value != rule["const"]:
        raise ValueError(f"{at}: unexpected constant")
    if "enum" in rule and value not in rule["enum"]:
        raise ValueError(f"{at}: value outside enum")
    if "type" in rule:
        names = rule["type"] if isinstance(rule["type"], list) else [rule["type"]]
        kinds = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
                 "string": lambda x: isinstance(x, str), "null": lambda x: x is None}
        if not any(kinds[name](value) for name in names):
            raise ValueError(f"{at}: wrong type")
    if isinstance(value, dict):
        required = set(rule.get("required", []))
        if not required <= value.keys():
            raise ValueError(f"{at}: missing {sorted(required - value.keys())}")
        properties = rule.get("properties", {})
        if rule.get("additionalProperties") is False and value.keys() - properties.keys():
            raise ValueError(f"{at}: extra {sorted(value.keys() - properties.keys())}")
        for key, child in value.items():
            if key in properties:
                validate_schema(child, properties[key], schema, f"{at}.{key}")
    elif isinstance(value, list):
        if len(value) < rule.get("minItems", 0):
            raise ValueError(f"{at}: too few items")
        for index, child in enumerate(value):
            validate_schema(child, rule.get("items", {}), schema, f"{at}[{index}]")
    elif isinstance(value, str):
        if len(value) < rule.get("minLength", 0):
            raise ValueError(f"{at}: too short")
        if "pattern" in rule and not re.search(rule["pattern"], value):
            raise ValueError(f"{at}: pattern mismatch")


class TextAndIds(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
                 "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self.ids: set[str] = set()
        self.by_id: dict[str, list[str]] = {}
        self.links_by_id: dict[str, list[str]] = {}
        self.canonical_urls: list[str] = []
        self.active: list[tuple[str, int]] = []
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "link" and attributes.get("rel") == "canonical" and attributes.get("href"):
            self.canonical_urls.append(attributes["href"])
        if tag not in self.VOID_TAGS:
            self.tags.append(tag)
        ident = attributes.get("id")
        if ident:
            self.ids.add(ident)
            self.by_id[ident] = []
            self.links_by_id[ident] = []
            self.active.append((ident, len(self.tags)))
        if tag == "a" and attributes.get("href"):
            for active_id, _ in self.active:
                self.links_by_id[active_id].append(attributes["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag not in self.tags:
            return
        depth = len(self.tags) - self.tags[::-1].index(tag)
        self.tags = self.tags[:depth - 1]
        self.active = [(ident, start) for ident, start in self.active if start < depth]

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        for ident, _ in self.active:
            self.by_id[ident].append(data)


def assert_schema_vocabulary(value: object) -> None:
    allowed = {"$schema", "$id", "title", "type", "additionalProperties", "required",
               "properties", "const", "enum", "items", "minItems", "minLength",
               "pattern", "$defs", "$ref", "oneOf"}
    if not isinstance(value, dict):
        return
    for key, child in value.items():
        if key not in allowed:
            raise ValueError(f"unsupported schema keyword: {key}")
        if key in ("properties", "$defs"):
            for subrule in child.values():
                assert_schema_vocabulary(subrule)
        elif key in ("items",):
            assert_schema_vocabulary(child)
        elif key == "oneOf":
            for subrule in child:
                assert_schema_vocabulary(subrule)


def deny_leaks(data: bytes, label: str) -> None:
    content = data.decode("utf-8")
    for marker in DENIED:
        if marker.search(content):
            raise ValueError(f"{label}: private-data marker")


def validate_contract(model: dict, schema: dict, repo: Path = ROOT) -> None:
    assert_schema_vocabulary(schema)
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError("schema dialect mismatch")
    validate_schema(model, schema, schema)
    deny_leaks(encoded(model), "source model")
    nodes = model["nodes"]
    by_id = {node["id"]: node for node in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate node ID")
    relations = model["relationships"]
    if len({edge["id"] for edge in relations}) != len(relations):
        raise ValueError("duplicate relationship ID")
    readers = [n for n in nodes if n["type"] == "Reader"]
    if not readers or not any(n["type"] == "Claim" for n in nodes):
        raise ValueError("Reader and Claim required")
    if any(not reader["id"].startswith("urn:ghostmesh-readers:reader:") for reader in readers):
        raise ValueError("Reader ID namespace mismatch")
    catalog = json.loads((repo / "content/catalog.json").read_text())
    expected_readers = {
        "urn:ghostmesh-readers:reader:" + entry["slug"]: entry
        for entry in catalog["readers"]
    }
    if {reader["id"] for reader in readers} != set(expected_readers):
        raise ValueError("knowledge Reader inventory differs from public catalog")
    parsed_pages: dict[str, tuple[str, TextAndIds]] = {}
    for reader in readers:
        entry = expected_readers[reader["id"]]
        if (reader["label"] != entry["title"] or
                reader["url"] != catalog["host"] + "/" + entry["slug"] + "/" or
                reader["source"]["path"] != "site/" + entry["slug"] + "/index.html"):
            raise ValueError("knowledge Reader identity differs from public catalog")
        path = reader["source"]["path"]
        page_path = (repo / path).resolve()
        if not page_path.is_relative_to((repo / "site").resolve()):
            raise ValueError("source path escapes site")
        page = page_path.read_bytes()
        if sha(page) != reader["source"]["sha256"]:
            raise ValueError(f"{path}: source hash mismatch")
        raw = page.decode("utf-8")
        parsed = TextAndIds()
        parsed.feed(raw)
        if reader["url"] not in parsed.canonical_urls:
            raise ValueError(f"{path}: canonical URL mismatch")
        parsed_pages[reader["id"]] = (raw, parsed)
    for node in nodes:
        if node["type"] == "Claim":
            if not node["id"].startswith("urn:ghostmesh-readers:claim:"):
                raise ValueError("Claim ID namespace mismatch")
            provenance = node["provenance"]
            reader = by_id.get(provenance["sourceNodeId"])
            if reader is None or reader["type"] != "Reader":
                raise ValueError("claim source must be a Reader")
            raw, parsed = parsed_pages[reader["id"]]
            if provenance["sourceFileSha256"] != reader["source"]["sha256"]:
                raise ValueError("claim source hash mismatch")
            if provenance["locator"][1:] not in parsed.ids:
                raise ValueError("claim source anchor missing")
            if node["statement"] not in " ".join(parsed.by_id[provenance["locator"][1:]]):
                raise ValueError("claim statement is not exact text at source anchor")
            if sha(node["statement"].encode()) != provenance["quoteSha256"]:
                raise ValueError("claim quote hash mismatch")
        elif node["type"] == "EvidenceSource":
            if not node["id"].startswith("urn:ghostmesh-readers:source:"):
                raise ValueError("EvidenceSource ID namespace mismatch")
            if sha(node["url"].encode()) != node["urlSha256"]:
                raise ValueError("evidence URL hash mismatch")
            if not any(node["url"] in raw for raw, _ in parsed_pages.values()):
                raise ValueError("evidence URL absent from Reader")
            if node["contentSha256"] is not None:
                raise ValueError("external content bytes are not in public custody")
    for edge in relations:
        if not edge["id"].startswith("urn:ghostmesh-readers:relationship:"):
            raise ValueError("relationship ID namespace mismatch")
        source = by_id.get(edge["from"])
        target = by_id.get(edge["to"])
        if source is None or source["type"] != "Claim" or target is None or target["type"] != "EvidenceSource":
            raise ValueError("only published Claim-to-EvidenceSource citations are allowed")
        provenance = edge["provenance"]
        claim_provenance = source["provenance"]
        if any(provenance[key] != claim_provenance[key] for key in
               ("sourceNodeId", "locator", "sourceFileSha256", "quoteSha256")):
            raise ValueError("relationship provenance must match claim")
        _, parsed = parsed_pages[provenance["sourceNodeId"]]
        if target["url"] not in parsed.links_by_id.get(provenance["locator"][1:], []):
            raise ValueError("citation target absent from claim source anchor")


def render_html(model: dict) -> bytes:
    """Render the source-only index inside the normalized Reader shell."""
    from generate_site import page

    readers = [n for n in model["nodes"] if n["type"] == "Reader"]
    claims = [n for n in model["nodes"] if n["type"] == "Claim"]
    citations = model["relationships"]
    by_id = {n["id"]: n for n in model["nodes"]}
    cards = []
    for reader in readers:
        claim_items = []
        for claim in claims:
            if claim["provenance"]["sourceNodeId"] != reader["id"]:
                continue
            evidence = [by_id[e["to"]] for e in citations if e["from"] == claim["id"]]
            links = " ".join(
                f'<a href="{html.escape(source["url"], quote=True)}" rel="noopener noreferrer">'
                f'{html.escape(source["label"])}</a>' for source in evidence
            )
            claim_items.append(
                f'<li id="{html.escape(claim["id"], quote=True)}" data-knowledge-id="{html.escape(claim["id"], quote=True)}">'
                f'<strong>{html.escape(claim["label"])}</strong>: {html.escape(claim["statement"])} '
                f'<small>Epistemic status: {html.escape(claim["epistemicStatus"])}. '
                f'Source: <a href="{html.escape(reader["url"] + claim["provenance"]["locator"], quote=True)}">'
                f'published evidence ledger</a>. External evidence: {links}.</small></li>'
            )
        detail = (f'<ul>{"".join(claim_items)}</ul>' if claim_items else
                  '<p>No claim citation is projected from this Reader in v0.1. '
                  'The Reader page and its own evidence receipt remain the source.</p>')
        cards.append(
            f'<article class="gm-card" data-knowledge-id="{html.escape(reader["id"], quote=True)}">'
            f'<h2><a href="{html.escape(reader["url"], quote=True)}">{html.escape(reader["label"])}</a></h2>'
            f'<p>Public Reader source. This source-only record does not certify factual truth or live deployment.</p>'
            f'{detail}</article>'
        )
    body = (
        '<header class="gm-intro"><p class="gm-kicker">Source-only reference / v0.1</p>'
        '<h1>Public knowledge data</h1><p>These records identify the public Reader pages. '
        'A claim and citation appear only when verified against exact published page text. '
        'This projection does not admit SharePlane Work relationships or certify an external report.</p></header>'
        '<p><a href="/knowledge/v0.1/readers.json">JSON</a> · '
        '<a href="/knowledge/v0.1/readers.jsonld">JSON-LD</a> · '
        '<a href="/knowledge/v0.1/contract.schema.json">Schema</a> · '
        '<a href="/knowledge/v0.1/publication-manifest.json">Publication manifest</a></p>'
        '<section id="knowledge-records" class="gm-cards" aria-label="Public Reader records">'
        + "".join(cards) + '</section>'
    )
    rendered = page('Public knowledge data', '/knowledge/', body)
    # The projection disallows email addresses even in the shared site footer.
    rendered = rendered.replace(' · <a href="mailto:ghostmesh@malott.ai">Contact GhostMesh</a>', '')
    return rendered.encode('utf-8')


def render_jsonld(model: dict) -> bytes:
    graph = []
    for node in model["nodes"]:
        mapped = {
            "@id": node["id"],
            "@type": {"Reader": "schema:Article", "Claim": "schema:CreativeWork",
                      "EvidenceSource": "schema:CreativeWork"}[node["type"]],
            "gm:nodeType": node["type"],
            "gm:visibility": node["visibility"],
            "gm:epistemicStatus": node["epistemicStatus"],
            "schema:name": node["label"],
        }
        if "url" in node:
            mapped["schema:url"] = node["url"]
        if node["type"] == "Claim":
            mapped["schema:text"] = node["statement"]
            mapped["gm:provenance"] = node["provenance"]
        if node["type"] == "EvidenceSource":
            mapped["gm:urlSha256"] = node["urlSha256"]
            mapped["gm:contentSha256"] = node["contentSha256"]
        graph.append(mapped)
    for edge in model["relationships"]:
        graph.append({"@id": edge["id"], "@type": "gm:SourceDeclaredCitation",
                      "gm:from": {"@id": edge["from"]}, "gm:to": {"@id": edge["to"]},
                      "gm:authority": edge["authority"], "gm:visibility": edge["visibility"],
                      "gm:provenance": edge["provenance"]})
    return encoded({"@context": {"schema": "https://schema.org/",
                                  "gm": f"{HOST}/knowledge/v0.1/vocab#",
                                  "contractVersion": "gm:contractVersion",
                                  "publicationMode": "gm:publicationMode",
                                  "sourceNodeId": {"@id": "gm:sourceNodeId", "@type": "@id"},
                                  "locator": "gm:locator",
                                  "sourceFileSha256": "gm:sourceFileSha256",
                                  "quoteSha256": "gm:quoteSha256"},
                    "contractVersion": model["contractVersion"], "publicationMode": model["publicationMode"],
                    "@graph": graph})


def outputs(model: dict, schema_bytes: bytes, source_bytes: bytes) -> dict[str, bytes]:
    rendered = {
        "site/knowledge/v0.1/contract.schema.json": schema_bytes,
        "site/knowledge/v0.1/readers.json": encoded(model),
        "site/knowledge/v0.1/readers.jsonld": render_jsonld(model),
        "site/knowledge/index.html": render_html(model),
        "site/.well-known/ghostmesh-knowledge.json": encoded({
            "contractVersion": "0.1.0", "publicationMode": "source-only",
            "human": f"{HOST}/knowledge/", "json": f"{HOST}/knowledge/v0.1/readers.json",
            "jsonld": f"{HOST}/knowledge/v0.1/readers.jsonld",
            "schema": f"{HOST}/knowledge/v0.1/contract.schema.json",
            "manifest": f"{HOST}/knowledge/v0.1/publication-manifest.json"
        }),
        "site/llms.txt": (f"# GhostMesh Readers\n\nSource-only public knowledge reference: {HOST}/knowledge/\n"
                          f"JSON: {HOST}/knowledge/v0.1/readers.json\n"
                          f"JSON-LD: {HOST}/knowledge/v0.1/readers.jsonld\n"
                          "Claims are attributed to their published Reader sources. External content is not hash-certified.\n").encode()
    }
    entries = [{"path": path, "sha256": sha(data), "bytes": len(data)}
               for path, data in sorted(rendered.items())]
    manifest = {
        "contractVersion": "0.1.0", "publicationMode": "source-only",
        "sourcePath": "knowledge/v0.1/readers.source.json", "sourceSha256": sha(source_bytes),
        "schemaPath": "knowledge/v0.1/contract.schema.json", "schemaSha256": sha(schema_bytes),
        "outputs": entries, "outputsDigest": sha(encoded(entries))
    }
    rendered["site/knowledge/v0.1/publication-manifest.json"] = encoded(manifest)
    return rendered


def run(check: bool = False, repo: Path = ROOT) -> dict[str, bytes]:
    source_bytes = (repo / SOURCE.relative_to(ROOT)).read_bytes()
    schema_bytes = (repo / SCHEMA.relative_to(ROOT)).read_bytes()
    model = json.loads(source_bytes)
    schema = json.loads(schema_bytes)
    validate_contract(model, schema, repo)
    rendered = outputs(model, schema_bytes, source_bytes)
    for path, data in rendered.items():
        deny_leaks(data, path)
        destination = repo / path
        if check:
            if not destination.is_file() or destination.read_bytes() != data:
                raise ValueError(f"{path}: missing or stale generated output")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    return rendered


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = run(args.check)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: source-only schema, hashes, provenance, privacy, {len(result)} deterministic outputs")
