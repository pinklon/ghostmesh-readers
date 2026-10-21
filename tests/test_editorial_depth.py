"""Adversarial contract fixtures; synthetic reviewers here are not real signoff."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from editorial_depth import AREAS, binding, validate_reader


class EditorialDepthGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "content/readers").mkdir(parents=True)
        (self.root / "content/editorial-depth").mkdir(parents=True)
        shutil.copy2(ROOT / "content/editorial-depth/legacy-policy.json", self.root / "content/editorial-depth/legacy-policy.json")
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        self.reader = copy.deepcopy(next(r for r in catalog["readers"] if r["slug"] == "the-boundary-is-bigger-than-the-box"))
        self.slug = self.reader["slug"]
        self.article = self.root / "content/readers" / f"{self.slug}.html"
        self.receipt_path = self.root / "content/editorial-depth" / f"{self.slug}.json"
        self.reader["editorialDepth"] = {"schemaVersion": 1, "receiptPath": f"content/editorial-depth/{self.slug}.json"}
        # Representative argument fixture. Only the external human decision can
        # call actual public prose substantively sufficient.
        self.article.write_text('''<section id="hardware"><h2>What the machine changes</h2><p>The speaker describes local inference as one route for keeping sensitive inputs close to their owner. <a href="https://www.youtube.com/watch?v=DwoWIf8f2yQ&amp;t=1155s">19:15</a> is a source assertion, while the vendor page establishes only a hardware class. Model quality and this configuration's network traffic remain unmeasured.</p></section><section id="performance"><h2>The counterargument</h2><p>A throughput demonstration is not a completed-work comparison. <a href="https://www.youtube.com/watch?v=DwoWIf8f2yQ&amp;t=1515s">25:15</a> reports a rate, but first-token wait, outcome quality and multiple users could change the conclusion. A controlled hosted route might meet stronger quality and recovery requirements.</p></section><section id="decision"><h2>A decision that can fail</h2><p><a href="https://www.youtube.com/watch?v=DwoWIf8f2yQ&amp;t=4230s">1:10:30</a> opens a hybrid path. Pin versions, run matched safe tasks, inspect egress and tools, and restore from backup. If the local option fails a prespecified quality or data-boundary threshold, revise the recommendation.</p></section>''')
        self.receipt = self.make_receipt()
        self.save_receipt()
        self.api = patch("editorial_depth._get_json", side_effect=self.github_record)
        self.api.start()

    def tearDown(self):
        self.api.stop()
        self.tmp.cleanup()

    def github_record(self, url):
        base = "https://api.github.com/repos/pinklon/ghostmesh-readers/pulls/99"
        if url == base:
            return {"number": 99, "user": {"login": "fixture-writer", "id": 1}}
        if url == base + "/reviews/77":
            r = self.receipt
            marker = (f"GhostMesh-Editorial-Acceptance: readerId={r['readerId']}; "
                      f"sourceAidSha256={r['sourceAidSha256']}; articleSha256={r['articleSha256']}; "
                      f"evidenceRevision={r['evidenceRevision']}")
            return {"id": 77, "pull_request_url": base, "state": "APPROVED",
                    "user": {"login": "fixture-reviewer", "id": 2}, "body": marker}
        raise ValueError("unrecognized fixture URL")

    def make_receipt(self):
        record = {"schemaVersion": 1, **binding(self.reader, self.article.read_bytes()),
                  "candidateAuthor": "fixture-writer",
                  "complexity": {"tier": "extended", "factors": ["95 minute source", "privacy and cost claims"], "rationale": "The long interview makes material performance, economic and privacy claims that warrant extended analysis."},
                  "sourceMap": [
                      {"atSeconds": 1155, "sectionId": "hardware", "claimIds": [self.reader["claims"][0]["id"]], "rationale": "The source describes a local configuration, but the article separates the speaker report from a measured outcome."},
                      {"atSeconds": 1515, "sectionId": "performance", "claimIds": [self.reader["claims"][1]["id"]], "rationale": "The rate claim is placed beside quality and latency gaps rather than presented as a controlled cloud result."},
                      {"atSeconds": 4230, "sectionId": "decision", "claimIds": [self.reader["claims"][2]["id"]], "rationale": "The hybrid discussion supports a conditional experiment and does not verify a privacy guarantee."},
                  ],
                  "assessment": {area: {"disposition": "covered", "rationale": f"The independent fixture reviewer assessed {area} against the three argument sections and the source map."} for area in AREAS},
                  "independentCorroboration": "none",
                  "reviewer": {"login": "fixture-reviewer", "pullNumber": 99, "reviewId": 77},
                  "decision": "accept", "gaps": [],
                  "decisionRationale": "This is a synthetic contract fixture for testing the accepted state, not a qualitative review of a real Reader.",
                  "assessedAt": "2026-10-21T00:00:00Z"}
        return record

    def save_receipt(self):
        self.receipt_path.write_text(json.dumps(self.receipt))

    def assert_rejected(self, term):
        self.save_receipt()
        errors = validate_reader(self.root, self.reader)
        self.assertTrue(any(term in error for error in errors), errors)

    def test_long_form_fixture_with_independent_acceptance_is_admitted(self):
        self.assertEqual([], validate_reader(self.root, self.reader))

    def test_schema_complete_but_reviewer_rejected_superficial_argument_is_held(self):
        self.receipt["decision"] = "revise"
        self.receipt["gaps"] = [{"type": "synthesis", "severity": "blocking", "rationale": "The sections repeat the episode's talking points without testing the consequential inference."}]
        self.assert_rejected("editorial release held")

    def test_short_legitimate_source_can_receive_brief_treatment(self):
        self.reader["source"]["durationSeconds"] = 95
        self.reader["architectureImpact"] = "watch"
        self.article.write_text('<section id="one"><p>At <a href="https://www.youtube.com/watch?v=DwoWIf8f2yQ&amp;t=15s">00:15</a>, the source states a narrow claim. The article marks that claim as an assertion and offers a qualified alternative and a test that could change the call.</p></section>')
        self.receipt = self.make_receipt()
        self.receipt["complexity"] = {"tier": "brief", "factors": ["95 second source", "narrow claim"], "rationale": "The short source makes one narrow claim, so a concise critical reading can cover its actual stakes."}
        self.receipt["sourceMap"] = [{"atSeconds": 15, "sectionId": "one", "claimIds": [self.reader["claims"][0]["id"]], "rationale": "The source location and the article identify the narrow assertion and an alternative explanation."}]
        self.save_receipt()
        self.assertEqual([], validate_reader(self.root, self.reader))

    def test_fabricated_timestamp_not_in_article_map_fails(self):
        self.receipt["sourceMap"][0]["atSeconds"] = 1900
        self.assert_rejected("timestamp absent")

    def test_metadata_only_change_retains_acceptance(self):
        self.reader["updated"] = "2026-10-21T00:10:00Z"
        self.assertEqual([], validate_reader(self.root, self.reader))

    def test_article_or_source_change_invalidates_review(self):
        self.article.write_text(self.article.read_text() + '<p>A new claim after review.</p>')
        self.assert_rejected("articleSha256 binding mismatch")
        self.article.write_text(self.article.read_text()[:-len('<p>A new claim after review.</p>')])
        self.reader["source"]["title"] = "Changed source identity"
        self.assert_rejected("sourceDigest binding mismatch")

    def test_evidence_change_invalidates_review(self):
        self.reader["claims"][0]["assessment"] = "Changed after signoff"
        self.assert_rejected("evidenceRevision binding mismatch")

    def test_vendor_only_refs_cannot_claim_independent_outcome(self):
        self.receipt["independentCorroboration"] = "qualified"
        self.assert_rejected("vendor-only or methodological")

    def test_self_review_and_placeholders_fail(self):
        self.receipt["reviewer"]["login"] = self.receipt["candidateAuthor"]
        self.assert_rejected("authenticated independent acceptance")
        self.receipt["reviewer"]["login"] = "fixture-reviewer"
        self.receipt["assessment"]["sourceCoverage"]["rationale"] = "TODO add analysis here with a long explanation later"
        self.assert_rejected("assessment missing or superficial")

    def test_fictitious_review_or_wrong_hash_marker_fails(self):
        self.receipt["reviewer"]["reviewId"] = 78
        self.assert_rejected("could not be verified")
        self.receipt["reviewer"]["reviewId"] = 77
        original = self.github_record
        with patch("editorial_depth._get_json", side_effect=lambda url: ({**original(url), "body": "Looks good"} if url.endswith("/reviews/77") else original(url))):
            self.assert_rejected("exact hash marker missing")

    def test_dismissed_review_or_same_github_actor_fails(self):
        original = self.github_record
        for changes in ({"state": "DISMISSED"}, {"user": {"login": "fixture-writer", "id": 1}}):
            with self.subTest(changes=changes):
                with patch("editorial_depth._get_json", side_effect=lambda url: ({**original(url), **changes} if url.endswith("/reviews/77") else original(url))):
                    self.assert_rejected("authenticated independent acceptance")

    def test_missing_exact_source_aid_digest_fails(self):
        self.reader["legacyReceipt"]["sourceInspection"].pop("transcriptExportSha256")
        self.receipt = self.make_receipt()
        self.assert_rejected("exact retained source-aid SHA-256 missing")

    def test_unrelated_video_link_cannot_ground_a_source_map(self):
        self.article.write_text(self.article.read_text().replace("watch?v=DwoWIf8f2yQ&amp;t=1155s", "watch?v=OtherVideoX&amp;t=1155s"))
        self.receipt = self.make_receipt()
        self.assert_rejected("exact video in mapped section")

    def test_source_link_in_another_section_cannot_ground_map(self):
        self.receipt["sourceMap"][0]["atSeconds"] = 1515
        self.assert_rejected("exact video in mapped section")

    def test_empty_or_placeholder_mapped_article_section_fails(self):
        self.article.write_text(self.article.read_text().replace('The speaker describes local inference as one route for keeping sensitive inputs close to their owner.', 'TODO add analysis here'))
        self.receipt = self.make_receipt()
        self.assert_rejected("ungrounded source/claim map entry")

    def test_empty_section_cannot_borrow_later_section_prose(self):
        self.article.write_text(self.article.read_text().replace('The speaker describes local inference as one route for keeping sensitive inputs close to their owner.', ''))
        self.article.write_text(self.article.read_text().replace('<section id="hardware"><h2>What the machine changes</h2><p>', '<section id="hardware"><h2>What the machine changes</h2><p></p><p>').replace(' <a href="https://www.youtube.com/watch?v=DwoWIf8f2yQ&amp;t=1155s">19:15</a> is a source assertion, while the vendor page establishes only a hardware class. Model quality and this configuration\'s network traffic remain unmeasured.</p></section>', '</p></section>'))
        self.receipt = self.make_receipt()
        self.assert_rejected("ungrounded source/claim map entry")

    def test_historical_exception_is_exact_and_not_quality_signoff(self):
        old = copy.deepcopy(self.reader)
        old.pop("editorialDepth")
        shutil.copy2(ROOT / "content/readers" / f"{self.slug}.html", self.article)
        self.assertEqual([], validate_reader(self.root, old))
        self.article.write_text(self.article.read_text() + "changed")
        self.assertTrue(any("historical editorial exception is stale" in x for x in validate_reader(self.root, old)))
        policy = json.loads((self.root / "content/editorial-depth/legacy-policy.json").read_text())
        self.assertIn("does not assert", policy["reviewDisposition"])

    def test_legacy_policy_cannot_be_silently_extended(self):
        policy_path = self.root / "content/editorial-depth/legacy-policy.json"
        policy = json.loads(policy_path.read_text())
        policy["readers"]["invented-slug"] = policy["readers"][self.slug]
        policy_path.write_text(json.dumps(policy))
        self.assertTrue(any("legacy policy missing or invalid" in x for x in validate_reader(self.root, self.reader)))

    def test_private_source_is_not_embedded_in_editorial_contract(self):
        for path in (ROOT / "content/editorial-depth").glob("*.json"):
            self.assertNotIn("/Users/", path.read_text())
            self.assertNotIn("YouTube transcript\n", path.read_text())


if __name__ == "__main__":
    unittest.main()
