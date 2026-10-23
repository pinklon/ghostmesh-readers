import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_late_arrival_identity_pilot import EVENTS,run
class LateArrivalTests(unittest.TestCase):
 def test_ledger_keeps_late_revisions_and_deduplicates(self):
  r=run()
  self.assertGreater(r["source_revision_ledger"]["accepted_count"],r["timestamp_cursor"]["accepted_count"])
  self.assertIn("paper-a@v2",r["source_revision_ledger"]["accepted"])
  self.assertIn("paper-c@v1",r["source_revision_ledger"]["duplicates"])
 def test_same_name_never_merged(self):
  r=run();alex=next(x for x in r["author_labels"] if x["display_name"]=="Alex Kim")
  self.assertFalse(alex["same_name_entity_merge_performed"])
  self.assertEqual(len(alex["explicit_authority_clusters"]),2)
  self.assertTrue(alex["unresolved_sources"])
 def test_explicit_id_can_group_without_collapsing_name(self):
  r=run();t=next(x for x in r["author_labels"] if x["display_name"]=="Taylor Chen")
  self.assertEqual(len(t["explicit_authority_clusters"]),1)
  self.assertEqual(len(t["explicit_authority_clusters"][0]["source_revisions"]),2)
 def test_out_of_order_events_rejected(self):
  events=list(EVENTS);events[2]=dict(events[2],arrived=1)
  with self.assertRaises(ValueError):run(events)
 def test_research_boundaries(self):
  r=run();self.assertFalse(r["outreach_authorized"]);self.assertEqual(r["production_adoption"],"NOT_AUTHORIZED")
if __name__=="__main__":unittest.main()
