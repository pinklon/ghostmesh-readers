import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_provider_diff import compare, SCHEMA


def snapshot(entries, status="observed", when="2026-10-22T00:00:00Z"):
    return {"schema": SCHEMA, "observed_at": when, "observations": [
        {"id": "openai-news", "provider": "OpenAI", "status": status, "entries": entries}]}


class ProviderDiffTests(unittest.TestCase):
    def test_new_entry_and_duplicate_url(self):
        first = snapshot([])
        second = snapshot([{"title": "Agents API", "url": "https://openai.com/index/devday-2026-recap/"},
                           {"title": "Agents API repost", "url": "https://openai.com/index/devday-2026-recap"}])
        result = compare(first, second)
        self.assertEqual(len(result["candidates"]), 1)
        self.assertEqual(result["candidates"][0]["kind"], "new-source-entry")
        self.assertEqual(result["publication_status"], "NOT_APPROVED")

    def test_unknown_source_is_not_zero_releases(self):
        result = compare(snapshot([{"title": "Decisions", "url": "https://openai.com/index/decisions-api/"}]),
                         snapshot([], status="unknown"))
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["source_health"][0]["status"], "UNKNOWN")

    def test_changed_title_requires_review(self):
        old = snapshot([{"title": "Preview", "url": "https://example.com/release"}])
        new = snapshot([{"title": "Generally available", "url": "https://example.com/release"}])
        result = compare(old, new)
        self.assertEqual(result["candidates"][0]["kind"], "changed-entry-title")
        self.assertEqual(result["candidates"][0]["editorial_status"], "NOT_APPROVED")

    def test_different_dates_do_not_reannounce(self):
        old = snapshot([{"title": "Decisions GA", "url": "https://openai.com/index/decisions-api/"}])
        new = snapshot([{"title": "Decisions GA", "url": "https://openai.com/index/decisions-api/"}],
                       when="2026-10-23T00:00:00Z")
        self.assertEqual(compare(old, new)["candidates"], [])

    def test_missing_source_and_bad_schema(self):
        self.assertEqual(compare(snapshot([]), {"schema": SCHEMA, "observations": []})["source_health"][0]["status"], "UNKNOWN")
        with self.assertRaises(ValueError):
            compare({"schema": "bad", "observations": []}, snapshot([]))


if __name__ == "__main__":
    unittest.main()
