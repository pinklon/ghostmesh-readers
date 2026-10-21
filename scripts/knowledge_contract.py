#!/usr/bin/env python3
"""Offline, source-only public projection. Uses only the Python standard library."""
from __future__ import annotations

import argparse
import copy
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


def sync_reader_nodes(source: dict, catalog: dict, repo: Path = ROOT) -> dict:
    """Refresh public Reader identity and page hashes; leave citations editorially admitted."""
    model = copy.deepcopy(source)
    entries = {"urn:ghostmesh-readers:reader:" + entry["slug"]: entry
               for entry in catalog["readers"]}
    existing = {node["id"]: node for node in model["nodes"] if node["type"] == "Reader"}
    if len(existing) != sum(node["type"] == "Reader" for node in model["nodes"]):
        raise ValueError("duplicate Reader node")
    if set(existing) - set(entries):
        raise ValueError("knowledge Reader no longer in public catalog")
    for ident, entry in entries.items():
        path = "site/" + entry["slug"] + "/index.html"
        page = (repo / path).resolve()
        if not page.is_relative_to((repo / "site").resolve()):
            raise ValueError("Reader source path escapes site")
        digest = sha(page.read_bytes())
        node = existing.get(ident)
        if node is None:
            node = {"id": ident, "type": "Reader", "visibility": "public",
                    "epistemicStatus": "source-editorial", "label": entry["title"],
                    "url": catalog["host"] + "/" + entry["slug"] + "/",
                    "source": {"path": path, "sha256": digest}}
            model["nodes"].append(node)
        else:
            node["label"] = entry["title"]
            node["url"] = catalog["host"] + "/" + entry["slug"] + "/"
            node["source"] = {"path": path, "sha256": digest}
    # Claim and citation hashes are deliberate admissions. A changed cited page
    # must fail validation until an editor checks the whole passage and rebinds it.
    return model


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


def build_claim_register(catalog: dict, model: dict, repo: Path = ROOT) -> dict:
    """Index every already-public editorial claim without admitting new graph citations."""
    readers = {n["id"].removeprefix("urn:ghostmesh-readers:reader:"): n
               for n in model["nodes"] if n["type"] == "Reader"}
    records = []
    for entry in catalog["readers"]:
        slug = entry["slug"]
        reader = readers[slug]
        parsed = TextAndIds()
        parsed.feed((repo / reader["source"]["path"]).read_text(encoding="utf-8"))
        references = {ref["id"]: ref for ref in entry["references"]}
        for claim in entry["claims"]:
            ident = claim["id"]
            if ident not in parsed.ids or claim["proposition"] not in " ".join(parsed.by_id[ident]):
                raise ValueError(f"{slug}/{ident}: published claim text or anchor differs from catalog")
            def mapped(ids: list[str]) -> list[dict]:
                result = []
                for ref_id in ids:
                    ref = references[ref_id]
                    anchor = "ref-" + ref_id
                    if anchor not in parsed.ids or ref["url"] not in parsed.links_by_id[anchor]:
                        raise ValueError(f"{slug}/{ident}: published reference differs from catalog")
                    result.append({key: ref[key] for key in ("id", "title", "url", "sourceType", "independence")})
                return result
            records.append({
                "readerSlug": slug, "readerTitle": entry["title"],
                "readerSha256": reader["source"]["sha256"], "id": ident,
                "claimUrl": f'{catalog["host"]}/{slug}/#{ident}',
                "proposition": claim["proposition"], "kind": claim["kind"],
                "status": claim["status"], "asOf": claim["asOf"],
                "sourceLocation": claim["sourceLocation"],
                "assessment": claim["assessment"], "limits": claim["limits"],
                "supportingReferences": mapped(claim["references"]),
                "counterevidence": mapped(claim["counterevidence"]),
            })
    statuses = {status: sum(r["status"] == status for r in records)
                for status in ("corroborated", "partially corroborated", "contradicted", "disputed", "unverified")}
    return {"contractVersion": model["contractVersion"], "projection": "published-editorial-claim-register",
            "scope": "Catalog assessments and links to exact published Reader anchors; reference links are not automatic corroboration or admitted v0.1 graph citations.",
            "readerCount": len(readers), "claimCount": len(records), "statusCounts": statuses, "claims": records}


def render_html(model: dict, catalog: dict, register: dict) -> bytes:
    """Render an explorable human view without broadening the source-only contract."""
    from generate_site import page
    from social_cards import approval, specs

    readers = [n for n in model["nodes"] if n["type"] == "Reader"]
    claims = [n for n in model["nodes"] if n["type"] == "Claim"]
    citations = model["relationships"]
    by_id = {n["id"]: n for n in model["nodes"]}
    catalog_by_slug = {entry["slug"]: entry for entry in catalog["readers"]}
    catalog_claims = [claim for reader in catalog["readers"] for claim in reader["claims"]]
    unverified = sum(claim["status"] == "unverified" for claim in catalog_claims)
    historical = sum(claim["status"] == "unverified" and claim["kind"] == "historical-ledger-entry" for claim in catalog_claims)
    material = sum(claim["status"] == "unverified" and claim["kind"] == "material-prose-claim" for claim in catalog_claims)
    claims_by_reader: dict[str, list[dict]] = {reader["id"]: [] for reader in readers}
    for claim in claims:
        claims_by_reader[claim["provenance"]["sourceNodeId"]].append(claim)
    source_count = sum(bool(items) for items in claims_by_reader.values())
    register_by_slug: dict[str, list[dict]] = {reader["slug"]: [] for reader in catalog["readers"]}
    for record in register["claims"]:
        register_by_slug[record["readerSlug"]].append(record)
    support_count = sum(bool(record["supportingReferences"]) for record in register["claims"])
    counter_count = sum(bool(record["counterevidence"]) for record in register["claims"])
    unverified_with_refs = sum(record["status"] == "unverified" and bool(record["supportingReferences"])
                               for record in register["claims"])
    rows = []
    for number, reader in enumerate(readers, 1):
        entry = catalog_by_slug[reader["id"].removeprefix("urn:ghostmesh-readers:reader:")]
        local_url = "/" + entry["slug"] + "/"
        source = entry["source"]
        if source.get("kind") == "paper":
            source_label = "Paper · " + source["publisher"]
        elif source.get("kind") == "article":
            source_label = "Article · " + source["publisher"]
        else:
            source_label = source["platform"] + (" · " + source["creator"] if source.get("creator") else "")
        claim_items = []
        for claim in claims_by_reader[reader["id"]]:
            evidence = [by_id[e["to"]] for e in citations if e["from"] == claim["id"]]
            links = ", ".join(f'<a href="{html.escape(source["url"], quote=True)}" rel="noopener noreferrer">'
                              f'{html.escape(source["label"])}</a>' for source in evidence)
            claim_items.append(
                f'<li id="{html.escape(claim["id"], quote=True)}" data-knowledge-id="{html.escape(claim["id"], quote=True)}">'
                f'<p class="kx-trace-label">{html.escape(claim["label"])}</p>'
                f'<blockquote>{html.escape(claim["statement"])}</blockquote>'
                f'<p class="kx-trace-meta">Status: {html.escape(claim["epistemicStatus"])}. '
                f'<a href="{html.escape(local_url + claim["provenance"]["locator"], quote=True)}">'
                f'Inspect the exact published passage</a>.</p>'
                f'<p class="kx-trace-meta">External source named there: {links or "none admitted"}. '
                'The link records attribution; external content bytes are not certified here.</p></li>'
            )
        trace = (f'<details class="kx-record-trace"><summary>Inspect {len(claim_items)} exact '
                 f'citation{"s" if len(claim_items) != 1 else ""} in this projection</summary>'
                 f'<ol>{"".join(claim_items)}</ol></details>' if claim_items else '')
        register_items = register_by_slug[entry["slug"]]
        def roles(references: list[dict]) -> str:
            return html.escape(", ".join(dict.fromkeys(ref["sourceType"] for ref in references)) or "none mapped")
        register_trace = ('<details class="kx-register-trace"><summary>Browse '
                          f'{len(register_items)} published claim assessments</summary><ol>' + ''.join(
                          '<li><span class="kx-register-status">'+html.escape(item["status"])+
                          '</span> <a href="'+html.escape(local_url+'#'+item["id"], quote=True)+'">'+
                          html.escape(item["proposition"])+
                          '</a><small>Claim role: '+html.escape(item["kind"])+
                          ' · Support roles: '+roles(item["supportingReferences"])+
                          ' · Counter roles: '+roles(item["counterevidence"])+
                          '</small></li>'
                          for item in register_items) + '</ol></details>')
        rows.append(
            f'<article class="kx-record" data-knowledge-id="{html.escape(reader["id"], quote=True)}" '
            f'data-trace="{"yes" if claim_items else "no"}">'
            f'<div class="kx-record-index"><span>{number:02d}</span><span>{html.escape(source_label)}</span></div>'
            '<div class="kx-record-body">'
            f'<h3><a href="{html.escape(local_url, quote=True)}">{html.escape(reader["label"])}</a></h3>'
            f'<p class="kx-record-overview">{html.escape(entry["overview"])}</p>'
            f'{register_trace}{trace}</div>'
            '<span class="kx-record-arrow" aria-hidden="true">↗</span></article>'
        )
    example = ''
    if claims:
        first = claims[0]
        source = by_id[first["provenance"]["sourceNodeId"]]
        example = (f'<a class="kx-feature-link" href="#{html.escape(first["id"], quote=True)}">'
                   f'<span>Trace an admitted citation</span><strong>{html.escape(first["label"])}</strong>'
                   f'<small>Open the exact statement in {html.escape(source["label"])} <span aria-hidden="true">↗</span></small></a>')
    body = (
        '<header class="kx-hero"><p class="gm-kicker">PUBLIC KNOWLEDGE / CONTRACT VERSION 0.1</p>'
        '<h1>Follow a claim<br>to its source.</h1>'
        '<p class="kx-hero-intro">This index identifies published Readers and the exact citations admitted to the public knowledge record. '
        'A source link tells you where a statement came from; it does not establish whether it is true.</p>'
        '<div class="kx-hero-actions"><a href="#knowledge-records">Browse source records ↓</a>'
        '<a href="#how-to-read">Understand the limits ↗</a></div></header>'
        '<section class="kx-overview" aria-label="Knowledge record summary">'
        f'<div class="kx-overview-numbers"><p><strong>{len(readers)}</strong><span>published Reader source records</span></p>'
        f'<p><strong>{len(claims)}</strong><span>exact-passage citations in the narrow v0.1 graph</span></p>'
        f'<p><strong>{len(catalog_claims)}</strong><span>published claim assessments indexed below</span></p>'
        f'<p><strong>{unverified}</strong><span>assessed as unverified, not false</span></p></div>'
        f'{example}</section>'
        '<section class="kx-reading-note" id="how-to-read"><div><p class="gm-kicker">READ THE RECORD</p>'
        '<h2>Attribution is the beginning of an inquiry.</h2></div>'
        '<div><p>Version 0.1 names the source-only data contract, not the maturity or truth of the Readers. '
        f'The {len(claims)} exact-passage citations are a deliberately narrow machine graph; they are not the denominator of public evidence. '
        f'All {len(catalog_claims)} published editorial claim assessments are indexed below and in the separate claim-register JSON. '
        f'{support_count} have a mapped supporting reference and {counter_count} have a mapped counterreference. '
        'A reference can be an original source, vendor account, independent study or other named role; a link is not an independent replication.</p>'
        '<p>Status and claim-role labels are the Readers’ dated editorial assessments, not new measurements by this index. '
        'A speaker report, an independent observation and a GhostMesh proposal carry different authority even when they share a topic. '
        'Inspect each claim’s mapped references, counterevidence and limits before treating a status as a settled conclusion.</p>'
        '<p>A projected graph citation binds a statement to an exact passage in a published Reader and, where listed, '
        'to the external source named there. Its authority is source-declared. It is not independent verification.</p>'
        f'<p>Of the {unverified} unverified register entries, {historical} are historical-ledger entries and {material} are material-prose claims. '
        f'{unverified_with_refs} still have mapped supporting references, which do not establish their full propositions. '
        'Unverified means the current public record does not establish the full proposition; it does not mean the statement is false. '
        'A source-fidelity check is different from independent corroboration.</p>'
        '<p>For dated corroboration, counterevidence and the editorial judgment, open the full Reader and its handling receipt. '
        '<a href="/the-score-is-not-the-system/#the-score-is-not-the-system--incident-counts">See a concrete example of qualified counts ↗</a></p>'
        '</div></section>'
        '<section class="kx-directory" id="knowledge-records" aria-label="Public Reader source records">'
        '<div class="kx-directory-head"><div><p class="gm-kicker">SOURCE DIRECTORY</p><h2>Explore the published record.</h2>'
        '<p>Open each record to browse its published claim assessments, evidence limits and the smaller exact-citation graph. '
        'The full reasoning and counterevidence remain in each Reader.</p></div>'
        f'<p class="kx-directory-scope">All {len(readers)} Readers have claim assessments; '
        f'{source_count} have an admitted exact citation in the narrow v0.1 graph.</p></div>'
        '<form class="kx-tools" data-knowledge-tools hidden role="search">'
        '<label for="kx-search">Find a Reader or statement</label><input id="kx-search" type="search" autocomplete="off" '
        'placeholder="Search this source directory" data-knowledge-query>'
        '<label for="kx-filter">Show</label><select id="kx-filter" data-knowledge-filter>'
        '<option value="all">All Reader sources</option><option value="yes">With exact citation</option>'
        '<option value="no">Without exact citation</option></select>'
        '<button type="reset">Clear</button></form>'
        f'<p class="kx-results" data-knowledge-results aria-live="polite">Showing all {len(readers)} Reader sources</p>'
        '<div class="kx-records">' + "".join(rows) + '</div>'
        '<p class="kx-empty" data-knowledge-empty hidden>No records match those filters. Clear the search to see every Reader.</p>'
        '</section>'
        '<footer class="kx-data-footer"><div><p class="gm-kicker">OPEN FORMATS</p><h2>Inspect the public data.</h2>'
        '<p>The narrow citation graph and the separate editorial claim register retain their distinct evidence roles. '
        'Neither export contains raw third-party media or transcripts.</p></div>'
        '<nav aria-label="Knowledge data downloads"><a href="/knowledge/v0.1/claim-register.json">All published claim assessments ↗</a>'
        '<a href="/knowledge/v0.1/readers.json">Narrow citation graph JSON ↗</a>'
        '<a href="/knowledge/v0.1/readers.jsonld">JSON-LD ↗</a>'
        '<a href="/knowledge/v0.1/contract.schema.json">Schema ↗</a>'
        '<a href="/knowledge/v0.1/publication-manifest.json">Publication manifest ↗</a></nav>'
        '<p>Want to explore related readings? <a href="/map/">Open the Reader connection map</a> '
        'or <a href="/map/relationships.json">inspect its separate editorial route JSON</a>. '
        'Its named editorial links help you navigate and do not prove a claim. '
        'Other sites, including SharePlane, need an explicit reviewed connection before appearing in this Reader graph.</p>'
        '</footer>'
    )
    rendered = page('Public knowledge data', '/knowledge/', body,
                    specs(catalog, preview_base=approval(ROOT).get("previewBaseUrl"))["/knowledge/"])
    rendered = rendered.replace('</head>', '<link rel="stylesheet" href="/assets/knowledge-explorer.css">'
                                '<script src="/assets/knowledge-explorer.js" defer></script></head>', 1)
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


def outputs(model: dict, schema_bytes: bytes, source_bytes: bytes,
            catalog: dict, register: dict) -> dict[str, bytes]:
    rendered = {
        "site/knowledge/v0.1/contract.schema.json": schema_bytes,
        "site/knowledge/v0.1/readers.json": encoded(model),
        "site/knowledge/v0.1/readers.jsonld": render_jsonld(model),
        "site/knowledge/v0.1/claim-register.json": encoded(register),
        "site/knowledge/index.html": render_html(model, catalog, register),
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
    catalog = json.loads((repo / "content/catalog.json").read_text(encoding="utf-8"))
    model = sync_reader_nodes(json.loads(source_bytes), catalog, repo)
    synced_source = (json.dumps(model, ensure_ascii=False, indent=2) + "\n").encode()
    schema = json.loads(schema_bytes)
    validate_contract(model, schema, repo)
    register = build_claim_register(catalog, model, repo)
    rendered = outputs(model, schema_bytes, synced_source, catalog, register)
    if check and source_bytes != synced_source:
        raise ValueError("knowledge Reader source inventory or page hashes stale")
    for path, data in rendered.items():
        deny_leaks(data, path)
    if not check and source_bytes != synced_source:
        (repo / SOURCE.relative_to(ROOT)).write_bytes(synced_source)
    for path, data in rendered.items():
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
