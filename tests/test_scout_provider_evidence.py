import copy
from hashlib import sha256
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_provider_diff import compare, entry_key, SCHEMA as OBSERVATION_SCHEMA
from scout_provider_evidence import capture, review_targets, visible_excerpt


REGISTRY = {"schema": "ghostmesh-scout-provider-sources-v1", "sources": [
    {"id": "openai-news", "provider": "OpenAI", "format": "rss",
     "url": "https://openai.com/news/rss.xml"},
    {"id": "anthropic-platform", "provider": "Anthropic", "format": "html",
     "url": "https://platform.claude.com/docs/en/release-notes/overview"},
]}
WHEN = "2026-10-24T12:00:00Z"


def observation(source, entries, payload=b"official observed bytes"):
    return {"id": source["id"], "provider": source["provider"],
            "source_url": source["url"], "status": "observed",
            "sha256": sha256(payload).hexdigest(), "entries": entries}


def snapshot(observations):
    present = {item["id"] for item in observations}
    observations = observations + [
        {"id": source["id"], "provider": source["provider"],
         "source_url": source["url"], "status": "unknown", "entries": []}
        for source in REGISTRY["sources"] if source["id"] not in present]
    return {"schema": OBSERVATION_SCHEMA, "observed_at": WHEN,
            "observations": observations}


class ProviderEvidenceTests(unittest.TestCase):
    def test_official_articles_are_distinct_and_metadata_is_not_a_launch_verdict(self):
        source = REGISTRY["sources"][0]
        prior = snapshot([observation(source, [{"title": "Earlier", "url": "https://openai.com/index/earlier/"}])])
        current_entries = [
            {"title": "Decisions API is generally available", "url": "https://openai.com/index/decisions-api/",
             "published": "Thu, 22 Oct 2026 00:00:00 GMT"},
            {"title": "Agents API announced at DevDay", "url": "https://openai.com/index/devday-2026-recap/",
             "published": "Wed, 21 Oct 2026 00:00:00 GMT"},
        ]
        current = snapshot([observation(source, prior["observations"][0]["entries"] + current_entries)])
        candidates = compare(prior, current)
        pages = {
            current_entries[0]["url"]: b"<main><h1>Decisions API</h1><p>Generally available on October 22.</p></main>",
            current_entries[1]["url"]: b"<main><h1>Agents API</h1><p>Announced at DevDay.</p></main>",
        }
        result = capture(candidates, current, REGISTRY, WHEN,
                         fetch_page=lambda source: (pages[source["url"]], source["url"]))
        self.assertEqual(len(result["records"]), 2)
        self.assertEqual({r["officialEvidenceUrl"] for r in result["records"]}, set(pages))
        self.assertEqual({r["candidateId"] for r in result["records"]},
                         {entry_key("openai-news", entry) for entry in current_entries})
        self.assertEqual({r["captureStatus"] for r in result["records"]}, {"captured"})
        for record in result["records"]:
            self.assertEqual(record["sourceScope"], "feed-entry-metadata-only")
            self.assertEqual(record["eventStatus"], "UNKNOWN")
            self.assertEqual(record["generalAvailability"], "UNKNOWN")
            self.assertEqual(record["accountEntitlement"], "UNKNOWN")
            self.assertEqual(record["editorialStatus"], "NOT_APPROVED")
        self.assertEqual(result["publicationStatus"], "NOT_APPROVED")
        self.assertEqual({entry["id"] for entry in result["sourceHealth"]},
                         {source["id"] for source in REGISTRY["sources"]})

    def test_changed_title_or_pricing_wording_is_not_an_approved_revision(self):
        source = REGISTRY["sources"][0]
        url = "https://openai.com/index/decisions-api/"
        old = snapshot([observation(source, [{"title": "Decisions preview", "url": url}])])
        new = snapshot([observation(source, [{"title": "Decisions GA and pricing update", "url": url}])])
        result = capture(compare(old, new), new, REGISTRY, WHEN,
                         fetch_page=lambda source: (b"<main><p>Provider page changed.</p></main>", source["url"]))
        self.assertEqual(result["records"][0]["changeKind"], "changed-entry-title")
        self.assertEqual(result["records"][0]["eventStatus"], "UNKNOWN")
        self.assertEqual(result["records"][0]["planEntitlement"], "UNKNOWN")

    def test_heading_change_is_page_only_and_stale_capture_is_explicit(self):
        source = REGISTRY["sources"][1]
        before = snapshot([observation(source, [{"level": "h2", "text": "Earlier release"}])])
        payload = b"<main><h2>New release</h2><p>A provider claim.</p></main>"
        after = snapshot([observation(source, [{"level": "h2", "text": "New release"}], payload)])
        candidates = compare(before, after)
        record = capture(candidates, after, REGISTRY, WHEN,
                         fetch_page=lambda source: (payload, source["url"]))["records"][0]
        self.assertEqual(record["captureStatus"], "captured")
        self.assertEqual(record["sourceScope"], "page-heading-change-only")
        self.assertEqual(record["excerptAnchors"], ["New release"])
        self.assertTrue(record["visibleExcerpt"].startswith("New release"))
        self.assertIsNone(record["capabilityIdentity"])
        self.assertEqual(record["eventStatus"], "UNKNOWN")
        stale = capture(candidates, after, REGISTRY, WHEN,
                        fetch_page=lambda source: (payload + b"<p>Later edit</p>", source["url"]))["records"][0]
        self.assertEqual(stale["captureStatus"], "STALE_SOURCE")
        self.assertNotEqual(stale["captureSha256"], stale["observedSourceSha256"])

    def test_source_outage_is_unknown_and_does_not_erase_other_candidates(self):
        source = REGISTRY["sources"][0]
        old = snapshot([observation(source, [{"title": "Earlier", "url": "https://openai.com/index/earlier/"}])])
        entries = [{"title": "Preview", "url": "https://openai.com/index/preview/"},
                   {"title": "Deprecation", "url": "https://openai.com/index/deprecation/"}]
        new = snapshot([observation(source, old["observations"][0]["entries"] + entries)])
        def fetch_page(item):
            if item["url"].endswith("preview/"):
                raise TimeoutError("private request internals must not be retained")
            return b"<article><h1>Deprecation</h1><p>Read the official notice.</p></article>", item["url"]
        records = capture(compare(old, new), new, REGISTRY, WHEN, fetch_page)["records"]
        self.assertEqual(len(records), 2)
        by_url = {r["officialEvidenceUrl"]: r for r in records}
        failed = by_url[entries[0]["url"]]
        self.assertEqual(failed["captureStatus"], "UNKNOWN")
        self.assertEqual(failed["errorType"], "TimeoutError")
        self.assertNotIn("private request internals", str(failed))
        self.assertEqual(by_url[entries[1]["url"]]["captureStatus"], "captured")

    def test_unapproved_host_or_unbound_candidate_is_rejected(self):
        source = REGISTRY["sources"][0]
        old = snapshot([observation(source, [{"title": "Earlier", "url": "https://openai.com/index/earlier/"}])])
        new = snapshot([observation(source, old["observations"][0]["entries"] +
                                    [{"title": "New", "url": "https://openai.com/index/new/"}])])
        candidates = compare(old, new)
        bad = copy.deepcopy(candidates)
        bad["candidates"][0]["url"] = "https://outside.example/claim"
        with self.assertRaises(ValueError):
            review_targets(bad, new, REGISTRY)
        bad = copy.deepcopy(candidates)
        bad["candidates"][0]["url"] = "https://github.blog/changelog/other-provider/"
        with self.assertRaises(ValueError):
            review_targets(bad, new, REGISTRY)
        bad = copy.deepcopy(candidates)
        bad["candidates"][0]["id"] = "unbound"
        with self.assertRaises(ValueError):
            review_targets(bad, new, REGISTRY)

    def test_heading_identity_and_full_source_matrix_are_required(self):
        source = REGISTRY["sources"][1]
        before = snapshot([observation(source, [{"level": "h2", "text": "Earlier"}])])
        after = snapshot([observation(source, [{"level": "h2", "text": "Later"}])])
        candidates = compare(before, after)
        bad = copy.deepcopy(candidates)
        bad["candidates"][0]["id"] = "false-heading-digest"
        with self.assertRaises(ValueError):
            review_targets(bad, after, REGISTRY)
        incomplete = copy.deepcopy(after)
        incomplete["observations"] = incomplete["observations"][:1]
        with self.assertRaises(ValueError):
            review_targets(compare(before, incomplete), incomplete, REGISTRY)

    def test_removed_historical_source_keeps_unknown_health_without_blocking_current_sources(self):
        source = REGISTRY["sources"][0]
        old = snapshot([observation(source, [{"title": "Earlier", "url": "https://openai.com/index/earlier/"}])])
        old["observations"].append({"id": "retired-source", "status": "observed", "entries": []})
        new = snapshot([observation(source, [{"title": "Earlier", "url": "https://openai.com/index/earlier/"},
                                              {"title": "New", "url": "https://openai.com/index/new/"}])])
        result = capture(compare(old, new), new, REGISTRY, WHEN,
                         fetch_page=lambda item: (b"<h1>New</h1>", item["url"]))
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(next(x for x in result["sourceHealth"] if x["id"] == "retired-source")["status"],
                         "UNKNOWN")

    def test_visible_excerpt_skips_scripts_and_is_bounded(self):
        text = visible_excerpt(b"<nav><p>Menu</p></nav><script>secret()</script>"
                               b"<main><h1>Official page</h1><p>Useful source context.</p></main>")
        self.assertEqual(text, "Official page\nUseful source context.")
        self.assertLessEqual(len(visible_excerpt(b"<p>" + b"word " * 10000 + b"</p>")), 2000)
        self.assertEqual(visible_excerpt(b"<h2>Old</h2><p>Old text</p>"
                                         b"<h2>New</h2><p>New text</p>", ["New"]),
                         "New\nNew text")
        self.assertEqual(visible_excerpt(
            b'<div hidden><div><p>Unreleased</p></div></div>'
            b'<p aria-hidden="true">Not visible</p>'
            b'<p style="display:\n none">Also hidden</p>'
            b'<template><p>Unpublished draft</p></template>'
            b'<main><p>Public notice</p></main>'), "Public notice")

    def test_redirect_to_different_page_never_looks_like_captured_evidence(self):
        source = REGISTRY["sources"][0]
        old = snapshot([observation(source, [{"title": "Earlier", "url": "https://openai.com/index/earlier/"}])])
        new = snapshot([observation(source, old["observations"][0]["entries"] +
                                    [{"title": "Decisions API", "url": "https://openai.com/index/decisions-api/"}])])
        result = capture(compare(old, new), new, REGISTRY, WHEN,
                         fetch_page=lambda _: (b"<h1>OpenAI news homepage</h1>",
                                               "https://openai.com/news/"))["records"][0]
        self.assertEqual(result["captureStatus"], "UNKNOWN")
        self.assertEqual(result["redirectStatus"], "DIFFERENT_SOURCE")
        self.assertEqual(result["visibleExcerpt"], "")
        self.assertEqual(result["eventStatus"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
