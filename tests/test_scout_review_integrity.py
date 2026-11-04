import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_review_integrity import verify

HASH = "a" * 40

def sample():
    cards = [{"review_id": f"SC-{i:02d}"} for i in range(21)]
    ratings = [{
        "review_id": row["review_id"],
        "ghostmesh_relevance": "ABSTAIN",
        "novelty": "ABSTAIN",
        "surprise": "ABSTAIN",
        "primary_source_inspected": False,
        "additional_source_opens": 1,
        "rationale": "Source material unavailable for review",
        "strongest_objection": "Primary claims cannot yet be verified",
        "source_review_sufficiency": "Source not accessed within budget"
    } for row in cards]
    return (
        {"schema": "scout-blind-review-packet-v0", "cards": cards},
        {"schema": "scout-independent-review-labels-v0",
         "packet": {"git_blob_sha": HASH}, "ratings": ratings}
    )

class ReviewIntegrityTests(unittest.TestCase):
    def test_accept_complete_without_unsealing(self):
        packet, review = sample()
        result = verify(packet, review, HASH)
        self.assertEqual(result["cases"], 21)
        self.assertFalse(result["cohort_unsealed"])

    def test_reject_packet_revision_mismatch(self):
        packet, review = sample()
        with self.assertRaises(ValueError):
            verify(packet, review, "b" * 40)

    def test_reject_duplicate_id(self):
        packet, review = sample()
        review["ratings"][1]["review_id"] = review["ratings"][0]["review_id"]
        with self.assertRaises(ValueError):
            verify(packet, review, HASH)

    def test_reject_over_budget_source_opens(self):
        packet, review = sample()
        review["ratings"][0]["additional_source_opens"] = 2
        with self.assertRaises(ValueError):
            verify(packet, review, HASH)

    def test_reject_invalid_score(self):
        packet, review = sample()
        review["ratings"][0]["ghostmesh_relevance"] = 4
        with self.assertRaises(ValueError):
            verify(packet, review, HASH)
