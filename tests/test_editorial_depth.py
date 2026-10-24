"""Adversarial fixtures; synthetic owner and agent records are not real signoff."""
import base64
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from editorial_depth import AREAS, _get_json, acceptance_marker, binding, validate_reader


class EditorialDepthGate(unittest.TestCase):
    def test_existing_contents_token_is_not_sent_to_public_pr_or_comment_reads(self):
        seen = []
        def response(request, timeout):
            seen.append((request.full_url, request.has_header("Authorization")))
            return io.BytesIO(b"{}")
        base = "https://api.github.com/repos/pinklon/ghostmesh-readers"
        with patch.dict(os.environ, {"GITHUB_TOKEN": "synthetic-test-token"}):
            with patch("editorial_depth.urlopen", side_effect=response):
                for path in ("/pulls/99", "/issues/comments/77", "/contents/content/catalog.json?ref=" + "a" * 40):
                    _get_json(base + path)
        self.assertEqual([False, False, True], [authorized for _, authorized in seen])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "content/readers").mkdir(parents=True)
        (self.root / "content/editorial-depth").mkdir(parents=True)
        (self.root / "content/source-maps").mkdir(parents=True)
        (self.root / "content/editorial-reviews").mkdir(parents=True)
        shutil.copy2(ROOT / "content/editorial-depth/legacy-policy.json", self.root / "content/editorial-depth/legacy-policy.json")
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        self.reader = copy.deepcopy(next(r for r in catalog["readers"] if r["slug"] == "the-boundary-is-bigger-than-the-box"))
        self.slug = self.reader["slug"]
        self.article = self.root / "content/readers" / f"{self.slug}.html"
        self.receipt_path = self.root / "content/editorial-depth" / f"{self.slug}.json"
        self.map_path = self.root / "content/source-maps" / f"{self.slug}.json"
        self.review_path = self.root / "content/editorial-reviews" / f"{self.slug}.json"
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
            return {"number": 99, "merged": False, "head": {"sha": "a" * 40},
                    "user": {"login": "fixture-writer", "id": 1}}
        if url == "https://api.github.com/repos/pinklon/ghostmesh-readers/issues/comments/77":
            r = self.receipt
            marker = acceptance_marker(r)
            return {"id": 77, "issue_url": "https://api.github.com/repos/pinklon/ghostmesh-readers/issues/99",
                    "author_association": "OWNER", "performed_via_github_app": None,
                    "created_at": "2026-10-21T00:02:00Z", "updated_at": "2026-10-21T00:02:00Z",
                    "user": {"login": "pinklon", "id": 10054714, "type": "User"}, "body": marker}
        prefix = "https://api.github.com/repos/pinklon/ghostmesh-readers/contents/"
        if url.startswith(prefix) and url.endswith("?ref=" + "a" * 40):
            path = unquote(urlsplit(url).path.split("/contents/", 1)[1])
            data = (json.dumps({"readers": [self.reader]}).encode() if path == "content/catalog.json"
                    else (self.root / path).read_bytes())
            return {"type": "file", "encoding": "base64", "size": len(data),
                    "content": base64.b64encode(data).decode()}
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
                  "ownerDecision": {"pullNumber": 99, "commentId": 77},
                  "decision": "accept", "gaps": [],
                  "decisionRationale": "This is a synthetic contract fixture for testing the accepted state, not a qualitative review of a real Reader.",
                  "assessedAt": "2026-10-21T00:00:00Z"}
        record["sourceMapEvidenceSha256"] = self.write_map(record)
        record["reviewEvidenceSha256"] = self.write_review(record)
        return record

    def write_review(self, record):
        data = {"schemaVersion": 1, "readerId": record["readerId"], "sourceId": record["sourceId"],
                "sourceAidSha256": record["sourceAidSha256"], "articleSha256": record["articleSha256"],
                "evidenceRevision": record["evidenceRevision"], "reviewedAt": "2026-10-21T00:01:00Z",
                "provenance": {"kind": "codex-task-agent",
                               "reference": "Synthetic fixture agent report in this local adversarial test, not a real reviewer identity.",
                               "limits": "This candidate-authored fixture record cannot authenticate any private agent's identity."},
                "summary": "The synthetic independent findings provide a testable record for the owner's separate decision.",
                "findings": [], "conclusion": "accept-for-owner-review"}
        self.review_path.write_text(json.dumps(data))
        return hashlib.sha256(self.review_path.read_bytes()).hexdigest()

    def write_map(self, record):
        points = [{"atSeconds": entry["atSeconds"], "sectionId": entry["sectionId"],
                   "claimIds": entry["claimIds"],
                   "cueParaphrase": "The synthetic cue describes only the topic and is not a claim of actual source verification.",
                   "privateAidCheck": "A separate fixture reviewer would compare this cue against the retained private aid."}
                  for entry in record["sourceMap"]]
        data = {"schemaVersion": 1, "readerId": record["readerId"], "sourceId": record["sourceId"],
                "sourceAidSha256": record["sourceAidSha256"], "points": points}
        self.map_path.write_text(json.dumps(data))
        return hashlib.sha256(self.map_path.read_bytes()).hexdigest()

    def save_receipt(self):
        self.receipt_path.write_text(json.dumps(self.receipt))

    def assert_rejected(self, term):
        self.save_receipt()
        errors = validate_reader(self.root, self.reader)
        self.assertTrue(any(term in error for error in errors), errors)

    def test_long_form_fixture_with_owner_acceptance_after_retained_findings_is_admitted(self):
        self.assertEqual([], validate_reader(self.root, self.reader))

    def test_local_only_skips_remote_owner_lookup_but_default_still_requires_it(self):
        with patch("editorial_depth._authenticated_owner_decision_errors", side_effect=RuntimeError("remote invoked")):
            self.assertEqual([], validate_reader(self.root, self.reader, verify_owner_remote=False))
            with self.assertRaisesRegex(RuntimeError, "remote invoked"):
                validate_reader(self.root, self.reader)

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
        self.receipt["sourceMapEvidenceSha256"] = self.write_map(self.receipt)
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

    def test_candidate_cannot_change_acceptance_or_assessment_after_owner_decision(self):
        approved = self.github_record("https://api.github.com/repos/pinklon/ghostmesh-readers/issues/comments/77")
        self.receipt["assessment"]["counterargument"]["rationale"] = "A different account of the counterargument was inserted after the submitted editorial review."
        with patch("editorial_depth._get_json", side_effect=lambda url: approved if url.endswith("/comments/77") else self.github_record(url)):
            self.assert_rejected("exact hash marker missing")

    def test_vendor_only_refs_cannot_claim_independent_outcome(self):
        self.receipt["independentCorroboration"] = "qualified"
        self.assert_rejected("vendor-only or methodological")

    def test_connector_posted_owner_comment_and_placeholders_fail(self):
        original = self.github_record
        with patch("editorial_depth._get_json", side_effect=lambda url: ({**original(url), "performed_via_github_app": {"slug": "chatgpt-codex-connector"}} if url.endswith("/comments/77") else original(url))):
            self.assert_rejected("authenticated unchanged owner acceptance")
        self.receipt["assessment"]["sourceCoverage"]["rationale"] = "TODO add analysis here with a long explanation later"
        self.assert_rejected("assessment missing or superficial")

    def test_fictitious_owner_comment_or_wrong_hash_marker_fails(self):
        self.receipt["ownerDecision"]["commentId"] = 78
        self.assert_rejected("could not be verified")
        self.receipt["ownerDecision"]["commentId"] = 77
        original = self.github_record
        with patch("editorial_depth._get_json", side_effect=lambda url: ({**original(url), "body": "Looks good"} if url.endswith("/comments/77") else original(url))):
            self.assert_rejected("exact hash marker missing")

    def test_no_owner_decision_remains_held(self):
        self.receipt["ownerDecision"] = None
        self.assert_rejected("authenticated owner decision locator missing")

    def test_owner_can_calculate_exact_pr_marker_before_comment_exists(self):
        self.receipt["ownerDecision"]["commentId"] = None
        self.assertIn("pullNumber=99", acceptance_marker(self.receipt))
        self.assert_rejected("authenticated owner decision locator missing")

    def test_wrong_open_pr_or_unmerged_main_release_fails(self):
        self.assertTrue(any("owner acceptance" in x for x in
                            validate_reader(self.root, self.reader, event_pr=98)))
        self.assertTrue(any("owner acceptance" in x for x in
                            validate_reader(self.root, self.reader, require_merged=True)))

    def test_same_author_comment_from_another_pr_cannot_be_replayed(self):
        old_marker = acceptance_marker(self.receipt)
        self.receipt["ownerDecision"]["pullNumber"] = 98
        original = self.github_record
        def wrong_pr(url):
            if url.endswith("/pulls/98"):
                return {"number": 98, "merged": False, "head": {"sha": "a" * 40},
                        "user": {"login": "fixture-writer", "id": 1}}
            if url.endswith("/comments/77"):
                return {**original(url), "issue_url": "https://api.github.com/repos/pinklon/ghostmesh-readers/issues/98",
                        "body": old_marker}
            return original(url)
        with patch("editorial_depth._get_json", side_effect=wrong_pr):
            self.assert_rejected("exact hash marker missing")

    def test_referenced_pr_must_contain_exact_accepted_artifacts(self):
        original = self.github_record
        path = f"/contents/content/readers/{self.slug}.html"
        def altered(url):
            item = original(url)
            if path in url:
                data = b"Different article in a same-author PR"
                return {**item, "size": len(data), "content": base64.b64encode(data).decode()}
            return item
        with patch("editorial_depth._get_json", side_effect=altered):
            self.assert_rejected("referenced PR does not contain the accepted artifacts")

    def test_merged_pr_has_durable_commit_proof_on_later_pr(self):
        original = self.github_record
        def merged(url):
            item = original(url)
            if url.endswith("/pulls/99"):
                return {**item, "merged": True, "merge_commit_sha": "a" * 40}
            return item
        with patch("editorial_depth._get_json", side_effect=merged):
            self.assertEqual([], validate_reader(self.root, self.reader, event_pr=100, require_merged=True))

    def test_edited_replayed_or_wrong_actor_decision_fails(self):
        original = self.github_record
        for changes in ({"updated_at": "2026-10-21T00:03:00Z"},
                        {"issue_url": "https://api.github.com/repos/pinklon/ghostmesh-readers/issues/98"},
                        {"created_at": "2026-10-21T00:00:00Z", "updated_at": "2026-10-21T00:00:00Z"},
                        {"user": {"login": "fixture-writer", "id": 1, "type": "User"}},
                        {"author_association": "NONE"}):
            with self.subTest(changes=changes):
                with patch("editorial_depth._get_json", side_effect=lambda url: ({**original(url), **changes} if url.endswith("/comments/77") else original(url))):
                    self.assert_rejected("authenticated unchanged owner acceptance")

    def test_quoted_or_negated_marker_is_not_acceptance(self):
        original = self.github_record
        with patch("editorial_depth._get_json", side_effect=lambda url: ({**original(url), "body": "I do not approve. " + original(url)["body"]} if url.endswith("/comments/77") else original(url))):
            self.assert_rejected("exact hash marker missing")

    def test_retained_findings_change_or_hold_invalidates_owner_acceptance(self):
        data = json.loads(self.review_path.read_text())
        data["summary"] = "An altered account of the agent's findings was inserted after the owner's exact decision."
        self.review_path.write_text(json.dumps(data))
        self.assert_rejected("retained qualitative findings digest mismatch")
        self.receipt["reviewEvidenceSha256"] = hashlib.sha256(self.review_path.read_bytes()).hexdigest()
        data["conclusion"] = "hold"
        self.review_path.write_text(json.dumps(data))
        self.receipt["reviewEvidenceSha256"] = hashlib.sha256(self.review_path.read_bytes()).hexdigest()
        self.assert_rejected("do not support owner acceptance")

    def test_retained_findings_reject_private_marker_with_fresh_digest(self):
        data = json.loads(self.review_path.read_text())
        data["summary"] += " Synthetic token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456 must stay private."
        self.review_path.write_text(json.dumps(data))
        self.receipt["reviewEvidenceSha256"] = hashlib.sha256(self.review_path.read_bytes()).hexdigest()
        self.assert_rejected("qualitative findings contain a private marker")

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

    def test_separate_source_map_cannot_drift_after_review(self):
        data = json.loads(self.map_path.read_text())
        data["points"][0]["atSeconds"] = 1900
        self.map_path.write_text(json.dumps(data))
        self.assert_rejected("separate source-map evidence digest mismatch")

    def test_receipt_cannot_reassign_claim_to_unchecked_cue(self):
        self.receipt["sourceMap"][0]["claimIds"] = [self.reader["claims"][3]["id"]]
        self.assert_rejected("source-map point lacks separately checked cue")

    def test_public_cue_map_rejects_private_marker_even_with_fresh_digest(self):
        data = json.loads(self.map_path.read_text())
        data["points"][0]["privateAidCheck"] += " Synthetic token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456 must never appear in public source maps."
        self.map_path.write_text(json.dumps(data))
        self.receipt["sourceMapEvidenceSha256"] = hashlib.sha256(self.map_path.read_bytes()).hexdigest()
        self.assert_rejected("contains a private marker")

    def test_instagram_and_paper_maps_require_original_source_link(self):
        self.reader["source"] = {"shortcode": "DeUnZhWgPKd", "url": "https://www.instagram.com/reel/DeUnZhWgPKd/", "durationSeconds": 5739}
        self.receipt = self.make_receipt()
        self.assert_rejected("lacks original source link")
        self.reader["source"] = {"kind": "paper", "identity": "doi:example", "url": "https://example.org/paper"}
        self.receipt = self.make_receipt()
        for entry in self.receipt["sourceMap"]:
            entry["atSeconds"] = None
        self.receipt["sourceMapEvidenceSha256"] = self.write_map(self.receipt)
        self.assert_rejected("lacks original source link")

    def test_extended_written_paper_uses_three_grounded_sections_without_fake_times(self):
        paper = next(r for r in json.loads((ROOT / "content/catalog.json").read_text())["readers"]
                     if r["source"].get("kind") == "paper")
        self.reader["source"] = copy.deepcopy(paper["source"])
        url = self.reader["source"]["url"]
        self.article.write_text(''.join(
            f'<section id="{section}"><h2>{section.title()}</h2><p>'
            f'The source gives a distinct, qualified claim for this part of the argument. '
            f'<a href="{url}">Original article</a> supports what the operator reports, '
            f'while independent outcome measurements and recovery tests remain unavailable here.</p></section>'
            for section in ("pressure", "architecture", "experiment")
        ))
        self.receipt = self.make_receipt()
        self.receipt["sourceMap"] = [
            {"atSeconds": None, "sectionId": section,
             "claimIds": [self.reader["claims"][index]["id"]],
             "rationale": "This written-source section separates the operator assertion from untested outcomes and records its original link."}
            for index, section in enumerate(("pressure", "architecture", "experiment"))
        ]
        self.receipt["sourceMapEvidenceSha256"] = self.write_map(self.receipt)
        self.save_receipt()
        self.assertEqual([], validate_reader(self.root, self.reader))
        self.receipt["sourceMap"][0]["atSeconds"] = 12
        self.assert_rejected("written source map must use section locators")

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
