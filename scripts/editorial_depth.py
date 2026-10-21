"""Hash-bound owner editorial decisions for Reader publication.

The checks prove that the reviewed source, evidence and authored HTML match the
candidate and that the owner posted an unchanged decision through GitHub without
the Codex connector. They cannot authenticate a private agent or judge prose.
"""
from __future__ import annotations

from datetime import datetime, timezone
import base64
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import quote
from urllib.request import Request, urlopen
from knowledge_contract import DENIED as PRIVATE_MARKERS

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
LEGACY_BINDINGS_SHA = "45eba2b01e6a1de5f89bbbe222f60a653265e0d554a3a2d23e4bc3a5129a9378"


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


def source_aid_sha256(reader: dict) -> str:
    """Digest of the retained private source aid, never its contents or local path."""
    receipt = reader.get("legacyReceipt") or {}
    pack = receipt.get("reasonPack") or {}
    if pack.get("verification") == "pass":
        return pack.get("manifestSha256", "")
    inspection = receipt.get("sourceInspection") or {}
    values = [value for key, value in inspection.items()
              if key.lower().endswith("sha256") and isinstance(value, str) and SHA.fullmatch(value)]
    return values[0] if len(values) == 1 else ""


def binding(reader: dict, authored_html: bytes) -> dict:
    return {
        "readerId": reader["id"],
        "sourceId": source_id(reader),
        "sourceDigest": digest(reader["source"]),
        "sourceAidSha256": source_aid_sha256(reader),
        "articleSha256": hashlib.sha256(authored_html).hexdigest(),
        "evidenceRevision": evidence_revision(reader),
    }


def assessment_digest(receipt: dict) -> str:
    """Bind candidate assessment bytes, excluding only the later owner comment locator."""
    return digest({key: value for key, value in receipt.items() if key != "ownerDecision"})


def acceptance_marker(receipt: dict) -> str:
    return (f"GhostMesh-Owner-Editorial-Acceptance: pullNumber={receipt['ownerDecision']['pullNumber']}; readerId={receipt['readerId']}; "
            f"sourceId={receipt['sourceId']}; sourceDigest={receipt['sourceDigest']}; "
            f"sourceAidSha256={receipt['sourceAidSha256']}; sourceMapEvidenceSha256={receipt['sourceMapEvidenceSha256']}; "
            f"reviewEvidenceSha256={receipt['reviewEvidenceSha256']}; articleSha256={receipt['articleSha256']}; "
            f"evidenceRevision={receipt['evidenceRevision']}; assessmentSha256={assessment_digest(receipt)}; decision=accept")


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


def _get_json(url: str) -> dict:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ghostmesh-editorial-gate"}
    # The existing Actions token has contents: read only. PRs and comments are
    # public reads; never send that token to endpoints outside its permission.
    if ("/contents/" in url or "/git/blobs/" in url) and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=8) as response:
        return json.load(response)


def _pr_file(path: str, ref: str) -> bytes:
    """Read a file at an immutable GitHub commit, rejecting truncated API replies."""
    url = f"https://api.github.com/repos/pinklon/ghostmesh-readers/contents/{quote(path)}?ref={ref}"
    item = _get_json(url)
    if item.get("type") != "file" or item.get("encoding") != "base64":
        raise ValueError("remote file body unavailable")
    payload = item.get("content")
    if not payload and item.get("size", 0) > 0:
        blob = _get_json(f"https://api.github.com/repos/pinklon/ghostmesh-readers/git/blobs/{item['sha']}")
        if blob.get("encoding") != "base64" or blob.get("sha") != item["sha"]:
            raise ValueError("remote blob body unavailable")
        payload = blob["content"]
    data = base64.b64decode(payload, validate=False)
    if len(data) != item.get("size"):
        raise ValueError("remote file body truncated")
    return data


def _authenticated_owner_decision_errors(root: Path, reader: dict, receipt: dict,
                                         review_evidence: dict | None, *, event_pr: int | None,
                                         require_merged: bool) -> list[str]:
    """Check Tony's GitHub comment, rejecting connector-posted or edited text."""
    slug = reader["slug"]
    locator = receipt["ownerDecision"]
    if (not isinstance(locator, dict) or set(locator) != {"pullNumber", "commentId"}
            or not isinstance(locator.get("pullNumber"), int) or isinstance(locator["pullNumber"], bool) or locator["pullNumber"] < 1
            or not isinstance(locator.get("commentId"), int) or isinstance(locator["commentId"], bool) or locator["commentId"] < 1):
        return [f"{slug}: authenticated owner decision locator missing"]
    number = locator["pullNumber"]
    base = f"https://api.github.com/repos/pinklon/ghostmesh-readers/pulls/{number}"
    try:
        pull = _get_json(base)
        comment = _get_json(f"https://api.github.com/repos/pinklon/ghostmesh-readers/issues/comments/{locator['commentId']}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"{slug}: authenticated owner decision could not be verified ({type(exc).__name__})"]
    author = pull.get("user") or {}
    user = comment.get("user") or {}
    marker = acceptance_marker(receipt)
    try:
        posted = datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00"))
        reviewed = datetime.fromisoformat(review_evidence["reviewedAt"].replace("Z", "+00:00"))
        assessed = datetime.fromisoformat(receipt["assessedAt"].replace("Z", "+00:00"))
        chronology_ok = all(value.tzinfo is not None for value in (posted, reviewed, assessed)) and posted >= max(reviewed, assessed)
    except (KeyError, TypeError, ValueError, AttributeError):
        chronology_ok = False
    if (pull.get("number") != number or comment.get("id") != locator["commentId"]
            or pull.get("merged") not in (True, False)
            or (require_merged and pull.get("merged") is not True)
            or (event_pr is not None and pull.get("merged") is False and number != event_pr)
            or comment.get("issue_url") != f"https://api.github.com/repos/pinklon/ghostmesh-readers/issues/{number}"
            or user.get("login") != "pinklon" or user.get("id") != 10054714 or user.get("type") != "User"
            or comment.get("author_association") != "OWNER"
            or "performed_via_github_app" not in comment or comment["performed_via_github_app"] is not None
            or not comment.get("created_at") or comment.get("created_at") != comment.get("updated_at")
            or not chronology_ok
            or author.get("login", "").casefold() != str(receipt["candidateAuthor"]).casefold()
            or (comment.get("body") or "").strip() != marker):
        return [f"{slug}: authenticated unchanged owner acceptance or exact hash marker missing"]
    ref = pull.get("merge_commit_sha") if pull["merged"] else (pull.get("head") or {}).get("sha")
    if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-f]{40}", ref):
        return [f"{slug}: referenced PR has no immutable artifact commit"]
    paths = (f"content/readers/{slug}.html", f"content/source-maps/{slug}.json",
             f"content/editorial-reviews/{slug}.json", f"content/editorial-depth/{slug}.json")
    try:
        if any(_pr_file(path, ref) != (root / path).read_bytes() for path in paths):
            return [f"{slug}: referenced PR does not contain the accepted artifacts"]
        catalog = json.loads(_pr_file("content/catalog.json", ref))
        remote = next(item for item in catalog["readers"] if item["id"] == reader["id"])
        if binding(remote, (root / paths[0]).read_bytes()) != binding(reader, (root / paths[0]).read_bytes()):
            return [f"{slug}: referenced PR catalog does not contain the accepted Reader"]
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        return [f"{slug}: referenced PR artifacts could not be verified ({type(exc).__name__})"]
    return []


def validate_reader(root: Path, reader: dict, *, release: bool = True,
                    event_pr: int | None = None, require_merged: bool = False) -> list[str]:
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
                or not isinstance(policy.get("readers"), dict) or len(policy["readers"]) != 26
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
    required = {"schemaVersion", *actual, "sourceMapEvidenceSha256", "reviewEvidenceSha256", "candidateAuthor", "complexity", "sourceMap", "assessment", "independentCorroboration", "ownerDecision", "decision", "gaps", "decisionRationale", "assessedAt"}
    if not isinstance(receipt, dict) or set(receipt) != required or receipt.get("schemaVersion") != 1:
        return errors + [f"{slug}: editorial receipt schema mismatch"]
    for key, value in actual.items():
        if receipt.get(key) != value:
            errors.append(f"{slug}: editorial {key} binding mismatch")
    for key in ("sourceDigest", "sourceAidSha256", "articleSha256", "evidenceRevision"):
        if not SHA.fullmatch(str(receipt.get(key, ""))):
            errors.append(f"{slug}: invalid editorial {key}")
    if not SHA.fullmatch(actual["sourceAidSha256"]):
        errors.append(f"{slug}: exact retained source-aid SHA-256 missing")
    map_path = root / "content" / "source-maps" / f"{slug}.json"
    try:
        map_bytes = map_path.read_bytes()
        map_evidence = json.loads(map_bytes)
    except (OSError, ValueError):
        map_evidence = None
        map_bytes = b""
        errors.append(f"{slug}: separate source-map evidence missing or invalid")
    if map_bytes and any(marker.search(map_bytes.decode("utf-8", "replace")) for marker in PRIVATE_MARKERS):
        errors.append(f"{slug}: separate source-map evidence contains a private marker")
    if not SHA.fullmatch(str(receipt.get("sourceMapEvidenceSha256", ""))) or hashlib.sha256(map_bytes).hexdigest() != receipt.get("sourceMapEvidenceSha256"):
        errors.append(f"{slug}: separate source-map evidence digest mismatch")
    review_path = root / "content" / "editorial-reviews" / f"{slug}.json"
    try:
        review_bytes = review_path.read_bytes()
        review_evidence = json.loads(review_bytes)
    except (OSError, ValueError):
        review_evidence = None
        review_bytes = b""
        errors.append(f"{slug}: retained qualitative findings record missing or invalid")
    if review_bytes and any(marker.search(review_bytes.decode("utf-8", "replace")) for marker in PRIVATE_MARKERS):
        errors.append(f"{slug}: retained qualitative findings contain a private marker")
    if not SHA.fullmatch(str(receipt.get("reviewEvidenceSha256", ""))) or hashlib.sha256(review_bytes).hexdigest() != receipt.get("reviewEvidenceSha256"):
        errors.append(f"{slug}: retained qualitative findings digest mismatch")
    if (not isinstance(review_evidence, dict)
            or set(review_evidence) != {"schemaVersion", "readerId", "sourceId", "sourceAidSha256", "articleSha256", "evidenceRevision", "reviewedAt", "provenance", "summary", "findings", "conclusion"}
            or review_evidence.get("schemaVersion") != 1
            or any(review_evidence.get(key) != actual[key] for key in ("readerId", "sourceId", "sourceAidSha256", "articleSha256", "evidenceRevision"))
            or not isinstance(review_evidence.get("provenance"), dict)
            or set(review_evidence["provenance"]) != {"kind", "reference", "limits"}
            or review_evidence["provenance"].get("kind") not in {"codex-task-agent", "external-human-report"}
            or not _reasoned(review_evidence["provenance"].get("reference"))
            or not _reasoned(review_evidence["provenance"].get("limits"))
            or not _reasoned(review_evidence.get("summary"))
            or review_evidence.get("conclusion") not in {"accept-for-owner-review", "revise", "hold"}
            or not isinstance(review_evidence.get("findings"), list)
            or any(not _reasoned(finding) for finding in review_evidence["findings"])):
        errors.append(f"{slug}: qualitative findings provenance or exact binding invalid")
    try:
        reviewed = datetime.fromisoformat(review_evidence["reviewedAt"].replace("Z", "+00:00"))
        if reviewed.tzinfo is None or reviewed > datetime.now(timezone.utc):raise ValueError
    except (TypeError, ValueError, AttributeError, KeyError):
        errors.append(f"{slug}: qualitative findings review date invalid")
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
        expected_points = [{key: entry.get(key) for key in ("atSeconds", "sectionId", "claimIds")}
                           for entry in source_map if isinstance(entry, dict)]
        if (not isinstance(map_evidence, dict) or set(map_evidence) != {"schemaVersion", "readerId", "sourceId", "sourceAidSha256", "points"}
                or map_evidence.get("schemaVersion") != 1 or map_evidence.get("readerId") != reader["id"]
                or map_evidence.get("sourceId") != source_id(reader) or map_evidence.get("sourceAidSha256") != actual["sourceAidSha256"]
                or not isinstance(map_evidence.get("points"), list) or len(map_evidence["points"]) != len(expected_points)):
            errors.append(f"{slug}: separate source-map identity or coverage mismatch")
        else:
            for point, expected in zip(map_evidence["points"], expected_points):
                if (not isinstance(point, dict) or set(point) != {"atSeconds", "sectionId", "claimIds", "cueParaphrase", "privateAidCheck"}
                        or any(point.get(key) != value for key, value in expected.items())
                        or not _reasoned(point.get("cueParaphrase")) or not _reasoned(point.get("privateAidCheck"))
                        or any(len(point[key]) > 500 or "\n" in point[key] or re.search(r"/Users/|/private/|transcript\\n", point[key], re.I)
                               for key in ("cueParaphrase", "privateAidCheck") if isinstance(point.get(key), str))):
                    errors.append(f"{slug}: source-map point lacks separately checked cue and claim grounding")
        claim_ids = {claim["id"] for claim in reader["claims"]}
        anchors = set(re.findall(r'\bid="([^"]+)"', raw.decode("utf-8", "replace")))
        article = raw.decode("utf-8", "replace")
        source_video = reader["source"].get("videoId")
        seen: set[tuple[int, str]] = set()
        for entry in source_map:
            if not isinstance(entry, dict) or set(entry) != {"atSeconds", "sectionId", "claimIds", "rationale"}:
                errors.append(f"{slug}: source map entry schema mismatch");continue
            second = entry["atSeconds"]
            section = re.search(r'<section\b[^>]*\bid="' + re.escape(str(entry["sectionId"])) + r'"[^>]*>(.*?)</section>', article, re.S)
            section_html = section.group(1) if section else ""
            links = [html.unescape(link) for link in re.findall(r'<a\b[^>]*href="([^"]+)"', section_html)]
            if reader["source"].get("kind") == "paper":
                if second is not None:
                    errors.append(f"{slug}: paper source map must use section locators rather than video time")
            elif not isinstance(second, int) or isinstance(second, bool) or second < 0 or (reader["source"].get("durationSeconds") and second >= reader["source"]["durationSeconds"]):
                errors.append(f"{slug}: source map timestamp absent from article or source duration")
            elif source_video:
                exact = (f"https://www.youtube.com/watch?v={source_video}&t={second}s",
                         f"https://youtu.be/{source_video}?t={second}s")
                if not any(link in exact for link in links):
                    errors.append(f"{slug}: source map timestamp absent from exact video in mapped section")
            if not source_video:
                source_url = reader["source"].get("url", "")
                if source_url not in links:
                    errors.append(f"{slug}: source map lacks original source link in mapped section")
                if isinstance(second, int) and not isinstance(second, bool):
                    label = f"{second // 60:02d}:{second % 60:02d}"
                    if label not in html.unescape(section_html):
                        errors.append(f"{slug}: non-YouTube source map timestamp absent from mapped section")
            if not isinstance(entry["sectionId"], str) or entry["sectionId"] not in anchors or not _mapped_prose(raw.decode("utf-8", "replace"), entry["sectionId"]) or not isinstance(entry["claimIds"], list) or not entry["claimIds"] or not all(isinstance(x, str) for x in entry["claimIds"]) or not set(entry["claimIds"]) <= claim_ids or not _reasoned(entry["rationale"]):
                errors.append(f"{slug}: ungrounded source/claim map entry")
            marker = (str(second), str(entry["sectionId"]))
            if marker in seen:errors.append(f"{slug}: duplicate source map point")
            seen.add(marker)
        if isinstance(complexity, dict) and complexity.get("tier") == "extended" and len({str(e.get("sectionId")) for e in source_map if isinstance(e, dict)}) < 3:
            errors.append(f"{slug}: extended source map misses distinct analytical sections")
        if isinstance(complexity, dict) and complexity.get("tier") == "extended" and len({e.get("atSeconds") for e in source_map if isinstance(e, dict)}) < 3:
            errors.append(f"{slug}: extended source map repeats a single source moment")
    if not isinstance(receipt["candidateAuthor"], str) or not receipt["candidateAuthor"].strip():
        errors.append(f"{slug}: accountable candidate author missing")
    if release and receipt.get("decision") == "accept" and not any("binding mismatch" in error for error in errors):
        if not isinstance(review_evidence, dict) or review_evidence.get("conclusion") != "accept-for-owner-review":
            errors.append(f"{slug}: retained qualitative findings do not support owner acceptance")
        errors.extend(_authenticated_owner_decision_errors(root, reader, receipt, review_evidence,
                                                           event_pr=event_pr, require_merged=require_merged))
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
