import unittest
from scripts.build_unified_search_index import build, public_url


def fixtures():
    readers = {"schema": "ghostmesh-public-reader-text-v1", "readerCount": 1,
               "readers": [{"id": "reader:one", "title": "One", "url": "/one/",
                            "category": "AI", "text": "Article text " * 12}]}
    share = {"schemaVersion": "shareplane.reader-public-works-snapshot.v1",
             "publicWorkCount": 1, "verifiedPublicRouteCount": 1,
             "sourceCatalogSha256": "a" * 64,
             "records": [{"id": "artifact:two", "title": "Two",
                          "canonicalUrl": "https://shareplane.malott.ai/artifacts/two/",
                          "publiclyAccessible": True, "published": False, "text": "A public summary"}]}
    return readers, share


class UnifiedIndexTests(unittest.TestCase):
    def test_build_and_source_types(self):
        result = build(*fixtures(), min_shareplane=1)
        self.assertEqual(len(result["records"]), 2)
        self.assertEqual({x["indexDepth"] for x in result["records"]}, {"full-text", "public-corpus"})

    def test_incomplete_coverage_fails(self):
        with self.assertRaisesRegex(ValueError, "coverage incomplete"):
            build(*fixtures())

    def test_public_historical_work_included(self):
        readers, share = fixtures()
        self.assertEqual(len(build(readers, share, min_shareplane=1)["records"]), 2)

    def test_duplicate_identity_fails(self):
        readers, share = fixtures()
        share["records"].append(dict(share["records"][0]))
        share["publicWorkCount"] = share["verifiedPublicRouteCount"] = 2
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            build(readers, share, min_shareplane=1)

    def test_missing_source_hash_rejected(self):\n        readers, share = fixtures()\n        del share["sourceCatalogSha256"]\n        with self.assertRaisesRegex(ValueError, "source hash"):\n            build(readers, share, min_shareplane=1)\n\n    def test_noncanonical_shareplane_route_rejected(self):\n        readers, share = fixtures()\n        share["records"][0]["canonicalUrl"] = "https://shareplane.malott.ai/admin/"\n        with self.assertRaisesRegex(ValueError, "non-canonical"):\n            build(readers, share, min_shareplane=1)\n\n    def test_untrusted_host_rejected(self):
        with self.assertRaises(ValueError):
            public_url("shareplane.malott.ai", "https://untrusted.example/path")

    def test_parent_route_rejected(self):
        with self.assertRaises(ValueError):
            public_url("shareplane.malott.ai", "../../private")

    def test_unverified_public_route_rejected(self):
        readers, share = fixtures()
        share["records"][0]["publiclyAccessible"] = False
        with self.assertRaisesRegex(ValueError, "unverified"):
            build(readers, share, min_shareplane=1)

    def test_shareplane_census_mismatch_rejected(self):
        readers, share = fixtures()
        share["publicWorkCount"] = 5
        with self.assertRaisesRegex(ValueError, "count mismatch"):
            build(readers, share, min_shareplane=1)


if __name__ == "__main__":
    unittest.main()
