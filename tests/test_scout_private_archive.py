import sys,json,tempfile,unittest,pathlib,hashlib,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_private_archive import verify_run,copy_verified,inventory
class ArchiveTests(unittest.TestCase):
 def sample(self,root):
  run=root/"original";run.mkdir(mode=0o700)
  blob=b"private Scout evidence";(run/"intake.json").write_bytes(blob);os.chmod(run/"intake.json",0o600)
  manifest={"schema":"scout-integrated-run-v0","run_id":"original",
   "publication_authorized":False,"outreach_authorized":False,
   "sha256":{"intake.json":hashlib.sha256(blob).hexdigest()},"sources":[],"leads":1}
  (run/"manifest.json").write_text(json.dumps(manifest));os.chmod(run/"manifest.json",0o600)
  return run
 def test_verified_backup_no_source_deletion(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);run=self.sample(root)
   dest=root/"backups"/"original"
   info=copy_verified(run,dest)
   self.assertTrue(info["sha256_verified"]);self.assertTrue(run.exists())
   self.assertEqual(verify_run(dest)["run_id"],"original")
   with self.assertRaises(FileExistsError):copy_verified(run,dest)
 def test_modified_bytes_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   run=self.sample(Path(temp));(run/"intake.json").write_text("tampered")
   with self.assertRaises(ValueError):verify_run(run)
 def test_inventory_never_prunes(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);self.sample(root)
   result=inventory(root)
   self.assertEqual(result["deleted"],0);self.assertEqual(len(result["runs"]),1)
 def test_world_readable_root_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)/"open";root.mkdir(mode=0o755)
   with self.assertRaises(PermissionError):inventory(root)
if __name__=="__main__":unittest.main()
