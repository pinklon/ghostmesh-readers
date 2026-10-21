"""A code-source Reader must stay pinned and inert, even when metadata is edited."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_site import validate_repository_source


class RepositorySourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        cls.source = next(reader["source"] for reader in catalog["readers"]
                          if reader["slug"] == "the-engine-is-not-the-service")
        cls.page = (ROOT / "site/the-engine-is-not-the-service/index.html").read_text()

    def test_pinned_source_has_direct_link_without_player(self):
        validate_repository_source(self.page, self.source)
        self.assertIn(self.source["url"], self.page)
        self.assertNotIn("gm-media-frame", self.page)

    def test_branch_or_partial_commit_cannot_replace_reviewed_source(self):
        for changed in (
            {"url": self.source["repositoryUrl"] + "/tree/main"},
            {"commit": self.source["commit"][:8]},
            {"repository": "deepseek-ai/AnotherRepo"},
        ):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate_repository_source(self.page, {**self.source, **changed})

    def test_compact_date_cannot_hide_predating_commit(self):
        with self.assertRaisesRegex(ValueError, "date"):
            validate_repository_source(self.page, {**self.source,
                "createdDate": "2026-10-20", "commitDate": "20261016"})

    def test_repacked_video_or_active_embed_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_repository_source(self.page, {**self.source, "mediaAspect": "16:9"})
        with self.assertRaises(ValueError):
            validate_repository_source(self.page + '<iframe src="https://example.test"></iframe>', copy.deepcopy(self.source))


if __name__ == "__main__":
    unittest.main()
