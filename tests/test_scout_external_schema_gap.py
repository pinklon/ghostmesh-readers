import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_external_schema_gap import audit
from scout_external_schema_gap import SCOUT_FIELDS
def data():
    case={f:"example" for f in SCOUT_FIELDS};case["id"]="a"
    a={"schema":"scout-connection-theses-v1","publication_authorized":False,"outreach_authorized":False,"theses":[case]}
    b={"schema":"scout-external-capability-comparison-v0","publication_authorized":False,"outreach_authorized":False,"candidates":[{"id":"bottleneck"},{"id":"inspectorraget"}]}
    return a,b
class ExternalAuditTests(unittest.TestCase):
 def test_unmapped_provenance(self):
    a,b=data();r=audit(a,b)
    self.assertIn("counterevidence",r["unmapped_fields_by_case"]["a"])
    self.assertIn("review_status",r["unmapped_fields_by_case"]["a"])
    self.assertFalse(r["externally_validated_import"])
 def test_reject_privilege(self):
    a,b=data();b["publication_authorized"]=True
    with self.assertRaises(ValueError):audit(a,b)
 def test_reject_missing_field(self):
    a,b=data();del a["theses"][0]["source_url"]
    with self.assertRaises(ValueError):audit(a,b)
 def test_source_pair_required(self):
    a,b=data();b["candidates"].pop()
    with self.assertRaises(ValueError):audit(a,b)
if __name__=="__main__":unittest.main()
