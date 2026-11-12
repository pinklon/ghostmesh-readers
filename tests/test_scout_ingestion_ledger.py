import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_ingestion_ledger import identity_revision,record_ledger
class LedgerTests(unittest.TestCase):
 def test_versions_are_distinct(self):
  x=record_ledger([{"url":"https://arxiv.org/abs/2610.28686v1"},
                   {"url":"https://arxiv.org/abs/2610.28686v2"},
                   {"url":"https://arxiv.org/abs/2610.28686v1"}])
  self.assertEqual(x["accepted"],2)
  self.assertEqual(x["duplicates"],1)
 def test_unversioned_does_not_claim_identical_content(self):
  x=record_ledger([{"url":"https://github.com/a/b"},{"url":"https://github.com/a/b"}])
  self.assertEqual(x["unverified_reobservations"],1)
 def test_late_revisions_not_dropped(self):
  x=record_ledger([{"url":"https://arxiv.org/abs/2610.28686v2"},
                   {"url":"https://arxiv.org/abs/2610.28686v1"}])
  self.assertEqual(x["accepted"],2)
 def test_author_name_is_unresolved(self):
  x=record_ledger([{"url":"https://arxiv.org/abs/2610.28686v1","author_name":"Alex Kim"}])
  self.assertEqual(x["receipts"][0]["person_identity"],"UNRESOLVED")
 def test_explicit_revision_conflict(self):
  with self.assertRaises(ValueError):identity_revision("https://arxiv.org/abs/2610.28686v1","v2")
 def test_hash_receipt(self):
  x=record_ledger([{"url":"https://github.com/a/b","capture_sha256":"a"*64}])
  self.assertTrue(x["receipts"][0]["source_content_verified"])
  self.assertEqual(x["receipts"][0]["revision"],"sha256:"+"a"*64)
 def test_prior_state(self):
  first=record_ledger([{"url":"https://arxiv.org/abs/2610.28686v1"}])
  second=record_ledger([{"url":"https://arxiv.org/abs/2610.28686v1"}],first["seen_keys"])
  self.assertEqual(second["duplicates"],1)
if __name__=="__main__":unittest.main()
