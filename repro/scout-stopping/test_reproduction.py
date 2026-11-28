"""Offline public reproduction tests. Invoke with python3 -B -m unittest discover."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / "run_reproduction.py"
SPEC = importlib.util.spec_from_file_location("scout_repro_runner", RUNNER)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class ReproductionTests(unittest.TestCase):
    def test_source_identity(self):
        runner.validate_sources()

    def test_expected_summary(self):
        runner.validate(runner.reports())

    def test_deterministic_repeat_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            first, second = Path(root) / "first", Path(root) / "second"
            a, b = runner.run(first), runner.run(second)
            self.assertEqual(a["outputs_sha256"], b["outputs_sha256"])
            self.assertEqual(sum(a["synthetic_rows"].values()), 912)
            with self.assertRaises(FileExistsError):
                runner.run(first)
            for name, digest in a["outputs_sha256"].items():
                self.assertEqual(runner.hashlib.sha256((first / name).read_bytes()).hexdigest(), digest)
            self.assertFalse(json.loads((first / "manifest.json").read_text())["production_adoption_authorized"])

    def test_mutated_fixture_is_rejected(self):
        normal = runner.search.TASK_TARGETS
        try:
            runner.search.TASK_TARGETS = (0,) + normal[1:]
            with self.assertRaises(AssertionError):
                runner.validate(runner.reports())
        finally:
            runner.search.TASK_TARGETS = normal


if __name__ == "__main__":
    unittest.main()
