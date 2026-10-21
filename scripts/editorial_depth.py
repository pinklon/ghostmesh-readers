"""Hash-bound human editorial decisions for Reader publication.

The checks prove that the reviewed source, evidence and authored HTML match the
candidate. They cannot decide whether the reviewer's argument is good.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

AREAS = (
    "sourceCoverage", "supportingArgument", "evidenceRoles", "counterargument",
    "tradeoffs", "falsifiability", "originalSynthesis", "performance",
    "economics", "threatGovernance",
)
DECISIONS = {"accept", "revise", "hold"}
GAP_TYPES = {"source", "claim", "evidence", "counterargument", "scope", "risk", "test", "synthesis"}
PLACEHOLDERS = re.compile(r"\b(?:TBD|TODO|lorem ipsum|add analysis here|placeholder)\b", re.I)
SHA = re.compile(r"[0-9a-f]{64}\Z")
LEGACY_BASELINE = "141a31c1fe9e44a07f9ccdf6f4471347dd13108b"
LEGACY_BINDINGS_SHA = "2382811aee95816946eb1fd0b30de06654833c1c4252584b046d81c6b2bc4f2a"


def digest(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def source_id(reader: dict) -> str:
    source = reader["source"]
    return source.get("videoId") or source.get("shortcode") or source.get("identity") or ""


def evidence_revision(reader: dict) -> str:
    """Editorial/evidence bytes; excludes clocks and presentation-only metadata."""
    keys = ("overview", "whyItMatters", "ghostMeshTakeaway", "falsification",
            "evidenceState", "claims", "references", "freshness")
    receipt = reader.get("legacyReceipt") or {}
    payload = {key: reader.get(key) for key in keys}
    payload["sourceInspection"] = receipt.get("sourceInspection")
    payload["custody"] = receipt.get("custody")
    return digest(payload)


def binding(reader: dict, authored_html: bytes) -> dict:
    return {
        "readerId": reader["id"],
        "sourceId": source_id(reader),
        "sourceDigest": digest(reader["source"]),
        "articleSha256": hashlib.sha256(authored_html).hexdigest(),
        "evidenceRevision": evidence_revision(reader),
    }


def _reasoned(value: object) -> bool:
    return isinstance(value, str) and len(value.strip()) >= 35 and not PLACEHOLDERS.search(value)


def _mapped_prose(raw: str, anchor: str) -> bool:
    """Catch empty/TODO mapped sections; the reviewer judges actual substance."""
    class Paragraphs(HTMLParser):
        VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.depth = 0
            self.p_depth = 0
            self.active = False
            self.parts: list[str] = []
            self.paragraphs: list[str] = []

        def handle_starttag(self, tag, attrs):
            if not self.active and dict(attrs).get("id") == anchor:
                self.active = True
                self.depth = 0
            if self.active and tag not in self.VOID:
                self.depth += 1
                if tag == "p" and not self.p_depth:
                    self.p_depth = self.depth
                    self.parts = []

        def handle_endtag(self, tag):
            if not self.active:
                return
            if tag == "p" and self.depth == self.p_depth:
                self.paragraphs.append(" ".join(self.parts).strip())
                self.p_depth = 0
            self.depth -= 1
            if self.depth <= 0:
                self.active = False

        def handle_data(self, data):
            if self.active and self.p_depth:
                self.parts.append(data)

    parsed = Paragraphs()
    parsed.feed(raw)
    return any(prose and not PLACEHOLDERS.search(prose) for prose in parsed.paragraphs)


def validate_reader(root: Path, reader: dict, *, release: bool = True) -> list[str]:
    """Validate one candidate or an unchanged, explicitly listed historical page."""
    slug = reader["slug"]
    article_path = root / "content" / "readers" / f"{slug}.html"
    if not article_path.is_file():
        return [f"{slug}: authored article missing"]
    raw = article_path.read_bytes()
    actual = binding(reader, raw)
    errors: list[str] = []
    policy_path = root / "content" / "editorial-depth" / "legacy-policy.json"
    try:
        policy = json.loads(policy_path.read_text())
        if (policy.get("schemaVersion") != 1 or policy.get("baselineCommit") != LEGACY_BASELINE
                or not isinstance(policy.get("readers"), dict)
                or digest(policy["readers"]) != LEGACY_BINDINGS_SHA):
            raise ValueError("legacy baseline changed")
        legacy = policy["readers"].get(slug)
    except (OSError, ValueError, KeyError, TypeError):
        return [f"{slug}: editorial legacy policy missing or invalid"]
    declaration = reader.get("editorialDepth")
    if declaration is None:
        if legacy is None:
            return [f"{slug}: editorial acceptance missing"]
        if actual != legacy:
            return [f"{slug}: historical editorial exception is stale; a new review receipt is required"]
        return []
    if not isinstance(declaration, dict) or declaration.get("schemaVersion") != 1:
        return [f"{slug}: editorial-depth declaration invalid"]
    if legacy is not None and actual == legacy:
        errors.append(f"{slug}: unchanged historical page must use the explicit legacy policy")
    expected_path = f"content/editorial-depth/{slug}.json"
    if declaration.get("receiptPath") != expected_path:
        errors.append(f"{slug}: editorial receipt path mismatch")
    try:
        receipt = json.loads((root / expected_path).read_text())
    except (OSError, ValueError):
        return errors + [f"{slug}: editorial receipt missing or invalid"]
    required = {"schemaVersion", *actual, "candidateAuthor", "complexity", "sourceMap", "assessment", "independentCorroboration", "reviewer", "decision", "gaps", "decisionRationale", "assessedAt"}
    if not isinstance(receipt, dict) or set(receipt) != required or receipt.get("schemaVersion") != 1:
        return errors + [f"{slug}: editorial receipt schema mismatch"]
    for key, value in actual.items():
        if receipt.get(key) != value:
            errors.append(f"{slug}: editorial {key} binding mismatch")
    for key in ("sourceDigest", "articleSha256", "evidenceRevision"):
        if not SHA.fullmatch(str(receipt.get(key, ""))):
            errors.append(f"{slug}: invalid editorial {key}")
    complexity = receipt["complexity"]
    if not isinstance(complexity, dict) or set(complexity) != {"tier", "factors", "rationale"} or complexity.get("tier") not in {"brief", "extended"} or not isinstance(complexity.get("factors"), list) or not complexity["factors"] or not _reasoned(complexity.get("rationale")):
        errors.append(f"{slug}: complexity disposition missing or superficial")
    else:
        duration = reader["source"].get("durationSeconds", 0)
        if (duration >= 1800 or len(reader["claims"]) >= 8 or reader["architectureImpact"] == "change proposed") and complexity["tier"] != "extended":
            errors.append(f"{slug}: consequential or long source requires extended editorial review")
    assessment = receipt["assessment"]
    if not isinstance(assessment, dict) or set(assessment) != set(AREAS):
        errors.append(f"{slug}: editorial assessment areas incomplete")
    else:
        for area, value in assessment.items():
            if not isinstance(value, dict) or set(value) != {"disposition", "rationale"} or value.get("disposition") not in {"covered", "gap", "not-applicable"} or not _reasoned(value.get("rationale")):
                errors.append(f"{slug}: {area} assessment missing or superficial")
            elif area in AREAS[:7] and value["disposition"] == "not-applicable":
                errors.append(f"{slug}: core {area} assessment cannot be not-applicable")
    if not isinstance(receipt["independentCorroboration"], str) or receipt["independentCorroboration"] not in {"none", "qualified"}:
        errors.append(f"{slug}: independent corroboration disposition invalid")
    elif receipt["independentCorroboration"] == "qualified":
        refs = {ref["id"]: ref for ref in reader["references"]}
        independent_types = {"randomized study", "original study", "independent investigation", "independent behavioral analysis on company-supplied data, scoped", "original measurements", "research paper", "research preprint", "historical research paper"}
        supported = any(claim.get("independentSourceCount", 0) > 0 and any(refs[ref_id]["sourceType"] in independent_types for ref_id in claim["references"] if ref_id in refs) for claim in reader["claims"])
        if not supported:
            errors.append(f"{slug}: vendor-only or methodological sources cannot certify independent outcome corroboration")
    source_map = receipt["sourceMap"]
    if not isinstance(source_map, list) or not source_map:
        errors.append(f"{slug}: source/claim map missing")
    else:
        claim_ids = {claim["id"] for claim in reader["claims"]}
        anchors = set(re.findall(r'\bid="([^"]+)"', raw.decode("utf-8", "replace")))
        source_links = {int(value) for value in re.findall(r"[?&](?:amp;)?t=(\d+)s", raw.decode("utf-8", "replace"))}
        seen: set[tuple[int, str]] = set()
        for entry in source_map:
            if not isinstance(entry, dict) or set(entry) != {"atSeconds", "sectionId", "claimIds", "rationale"}:
                errors.append(f"{slug}: source map entry schema mismatch");continue
            second = entry["atSeconds"]
            if reader["source"].get("kind") == "paper":
                if second is not None:
                    errors.append(f"{slug}: paper source map must use section locators rather than video time")
            elif not isinstance(second, int) or isinstance(second, bool) or second < 0 or (reader["source"].get("durationSeconds") and second >= reader["source"]["durationSeconds"]) or second not in source_links:
                errors.append(f"{slug}: source map timestamp absent from article or source duration")
            if not isinstance(entry["sectionId"], str) or entry["sectionId"] not in anchors or not _mapped_prose(raw.decode("utf-8", "replace"), entry["sectionId"]) or not isinstance(entry["claimIds"], list) or not entry["claimIds"] or not all(isinstance(x, str) for x in entry["claimIds"]) or not set(entry["claimIds"]) <= claim_ids or not _reasoned(entry["rationale"]):
                errors.append(f"{slug}: ungrounded source/claim map entry")
            marker = (str(second), str(entry["sectionId"]))
            if marker in seen:errors.append(f"{slug}: duplicate source map point")
            seen.add(marker)
        if isinstance(complexity, dict) and complexity.get("tier") == "extended" and len({str(e.get("sectionId")) for e in source_map if isinstance(e, dict)}) < 3:
            errors.append(f"{slug}: extended source map misses distinct analytical sections")
    reviewer = receipt["reviewer"]
    if not isinstance(receipt["candidateAuthor"], str) or not receipt["candidateAuthor"].strip():
        errors.append(f"{slug}: accountable candidate author missing")
    if not isinstance(reviewer, dict) or set(reviewer) != {"name", "role", "independentFromAuthor", "evidenceUrl"} or not all(isinstance(reviewer.get(k), str) and reviewer[k].strip() for k in ("name", "role", "evidenceUrl")) or reviewer.get("independentFromAuthor") is not True or not str(reviewer.get("evidenceUrl", "")).startswith("https://"):
        errors.append(f"{slug}: independent qualitative review evidence missing")
    elif isinstance(receipt["candidateAuthor"], str) and reviewer["name"].casefold().strip() == receipt["candidateAuthor"].casefold().strip():
        errors.append(f"{slug}: author cannot self-certify qualitative acceptance")
    gaps = receipt["gaps"]
    if not isinstance(gaps, list) or any(not isinstance(g, dict) or set(g) != {"type", "severity", "rationale"} or g.get("type") not in GAP_TYPES or g.get("severity") not in {"blocking", "nonblocking"} or not _reasoned(g.get("rationale")) for g in gaps):
        errors.append(f"{slug}: typed editorial gaps invalid")
    if not _reasoned(receipt["decisionRationale"]):
        errors.append(f"{slug}: editorial decision rationale missing or superficial")
    try:
        assessed = datetime.fromisoformat(receipt["assessedAt"].replace("Z", "+00:00"))
        if assessed.tzinfo is None or assessed > datetime.now(timezone.utc):raise ValueError
    except (TypeError, ValueError, AttributeError):
        errors.append(f"{slug}: editorial decision date invalid")
    if not isinstance(receipt["decision"], str) or receipt["decision"] not in DECISIONS:
        errors.append(f"{slug}: editorial decision invalid")
    blocking_gaps = not isinstance(gaps, list) or any(g.get("severity") == "blocking" for g in gaps if isinstance(g, dict))
    assessment_gaps = isinstance(assessment, dict) and any(v.get("disposition") == "gap" for v in assessment.values() if isinstance(v, dict))
    if release and (receipt["decision"] != "accept" or blocking_gaps or assessment_gaps):
        errors.append(f"{slug}: editorial release held by qualitative decision or unresolved gap")
    return errors
