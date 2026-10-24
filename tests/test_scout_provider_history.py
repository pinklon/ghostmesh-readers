import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_provider_history import select_artifact


def run(identifier, when, event="schedule", conclusion="success"):
    return {"id": identifier, "created_at": when, "event": event,
            "head_branch": "main", "conclusion": conclusion}


class ProviderHistoryTests(unittest.TestCase):
    def test_chooses_latest_retained_successful_main_snapshot(self):
        runs = [run(13, "2026-10-24T15:00:00Z"),
                run(12, "2026-10-23T15:00:00Z", event="workflow_dispatch"),
                run(11, "2026-10-22T15:00:00Z"),
                run(10, "2026-10-21T15:00:00Z")]
        artifacts = {13: [{"id": 113, "name": "scout-provider-observations-13", "expired": True}],
                     12: [{"id": 112, "name": "scout-provider-observations-12", "expired": False}],
                     11: [{"id": 111, "name": "other", "expired": False}],
                     10: [{"id": 110, "name": "scout-provider-observations-10", "expired": False}]}
        self.assertEqual(select_artifact(runs, lambda identifier: artifacts[identifier], 14),
                         {"run_id": 12, "artifact_id": 112})

    def test_no_prior_snapshot_is_explicitly_absent(self):
        runs = [run(14, "2026-10-25T15:00:00Z"),
                run(13, "2026-10-24T15:00:00Z", conclusion="failure")]
        self.assertIsNone(select_artifact(runs, lambda identifier: [], 14))

    def test_non_main_run_cannot_become_baseline(self):
        other = run(13, "2026-10-24T15:00:00Z", event="workflow_dispatch")
        other["head_branch"] = "topic"
        self.assertIsNone(select_artifact([other], lambda identifier: [
            {"id": 113, "name": "scout-provider-observations-13", "expired": False}], 14))

    def test_current_run_is_never_its_own_baseline(self):
        current = run(14, "2026-10-25T15:00:00Z")
        future = run(15, "2026-10-26T15:00:00Z")
        self.assertIsNone(select_artifact([current, future], lambda identifier: [
            {"id": identifier + 100, "name": f"scout-provider-observations-{identifier}",
             "expired": False}], 14))


if __name__ == "__main__":
    unittest.main()
