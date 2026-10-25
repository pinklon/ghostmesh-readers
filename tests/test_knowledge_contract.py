import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from sys import path as sys_path
sys_path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from knowledge_contract import ROOT, SCHEMA, SOURCE, build_claim_register, run, validate_contract


class KnowledgeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text())
        cls.model = json.loads(SOURCE.read_text())

    def invalid(self, change, reason=None):
        model = copy.deepcopy(self.model)
        change(model)
        with self.assertRaisesRegex(ValueError, reason or "."):
            validate_contract(model, self.schema)

    def test_reference_is_source_backed(self):
        validate_contract(self.model, self.schema)
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        self.assertEqual(len([node for node in self.model["nodes"] if node["type"] == "Reader"]), len(catalog["readers"]))
        self.assertTrue(any(node["id"] == "urn:ghostmesh-readers:claim:html-artifact-readability-report"
                            for node in self.model["nodes"]))
        self.assertTrue(any(edge["id"] == "urn:ghostmesh-readers:relationship:html-readability-cites-author"
                            for edge in self.model["relationships"]))
        self.assertIn("urn:ghostmesh-readers:reader:the-experiment-ran-did-the-research-advance",
                      {node["id"] for node in self.model["nodes"]})
        self.invalid(lambda m: m["nodes"].__setitem__(
            slice(None), [node for node in m["nodes"] if node["id"] !=
                          "urn:ghostmesh-readers:reader:the-experiment-ran-did-the-research-advance"]),
            "Reader inventory")

    def test_full_public_claim_register_reconciles_with_catalog_and_published_anchors(self):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        register = build_claim_register(catalog, self.model)
        source_claims = [claim for reader in catalog["readers"] for claim in reader["claims"]]
        self.assertEqual(register["readerCount"], len(catalog["readers"]))
        self.assertEqual(register["claimCount"], len(source_claims))
        self.assertEqual({item["id"] for item in register["claims"]},
                         {claim["id"] for claim in source_claims})
        self.assertEqual(register["statusCounts"]["unverified"],
                         sum(claim["status"] == "unverified" for claim in source_claims))
        self.assertEqual(sum(register["statusCounts"].values()), len(source_claims))
        self.assertLess(len(self.model["relationships"]), len(source_claims))  # A distinct narrow graph.
        public = json.loads((ROOT / "site/knowledge/v0.1/claim-register.json").read_text())
        self.assertEqual(public, register)
        for item in register["claims"]:
            self.assertTrue(item["claimUrl"].endswith('/'+item["readerSlug"]+'/#'+item["id"]))
        changed = copy.deepcopy(catalog)
        changed["readers"][0]["claims"][0]["proposition"] = "An invented public claim"
        with self.assertRaisesRegex(ValueError, "published claim text"):
            build_claim_register(changed, self.model)

    def test_new_reader_and_claim_require_regeneration_then_update_all_counts(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            catalog = json.loads((ROOT / "content/catalog.json").read_text())
            for rel in ("knowledge/v0.1/readers.source.json", "knowledge/v0.1/contract.schema.json"):
                target = repo / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
            for node in self.model["nodes"]:
                if node["type"] == "Reader":
                    rel = node["source"]["path"]
                    target = repo / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / rel, target)

            entry = copy.deepcopy(catalog["readers"][0])
            old_slug = entry["slug"]
            entry["slug"] = "projection-fixture"
            entry["id"] = "reader:projection-fixture"
            entry["title"] = "Projection fixture"
            entry["overview"] = "A new published Reader used to test automatic knowledge indexing."
            entry["references"] = []
            entry["claims"] = [copy.deepcopy(entry["claims"][0])]
            entry["claims"][0].update({"id": "projection-fixture--claim",
                                         "proposition": "A fixture claim in the published Reader.",
                                         "references": [], "counterevidence": [],
                                         "status": "unverified"})
            catalog["readers"].append(entry)
            (repo / "content").mkdir()
            (repo / "content/catalog.json").write_text(json.dumps(catalog))
            page = (repo / "site" / old_slug / "index.html").read_text()
            page = page.replace(catalog["host"] + "/" + old_slug + "/",
                                catalog["host"] + "/projection-fixture/", 1)
            page = page.replace("</body>", '<article id="projection-fixture--claim">'
                                'A fixture claim in the published Reader.</article></body>')
            target = repo / "site/projection-fixture/index.html"
            target.parent.mkdir(parents=True)
            target.write_text(page)

            with self.assertRaisesRegex(ValueError, "Reader source inventory or page hashes stale"):
                run(check=True, repo=repo)
            generated = run(repo=repo)
            register = json.loads(generated["site/knowledge/v0.1/claim-register.json"])
            graph = json.loads(generated["site/knowledge/v0.1/readers.json"])
            self.assertEqual(register["readerCount"], len(catalog["readers"]))
            self.assertEqual(register["claimCount"], sum(len(r["claims"]) for r in catalog["readers"]))
            self.assertEqual(register["statusCounts"]["unverified"],
                             sum(c["status"] == "unverified" for r in catalog["readers"] for c in r["claims"]))
            self.assertEqual(len(graph["relationships"]), len(self.model["relationships"]))  # No automatic citation admission.
            self.assertEqual(generated, run(check=True, repo=repo))
            uncited_page = repo / "site/projection-fixture/index.html"
            uncited_page.write_text(uncited_page.read_text() + " ")
            with self.assertRaisesRegex(ValueError, "Reader source inventory or page hashes stale"):
                run(check=True, repo=repo)
            rehashed = run(repo=repo)
            refreshed_graph = json.loads(rehashed["site/knowledge/v0.1/readers.json"])
            refreshed = next(node for node in refreshed_graph["nodes"] if node["id"] ==
                             "urn:ghostmesh-readers:reader:projection-fixture")
            self.assertEqual(refreshed["source"]["sha256"], hashlib.sha256(uncited_page.read_bytes()).hexdigest())
            self.assertEqual(rehashed, run(check=True, repo=repo))
            cited_page = repo / "site/the-inbox-was-a-boundary/index.html"
            cited_page.write_text(cited_page.read_text() + " ")
            with self.assertRaisesRegex(ValueError, "claim source hash mismatch"):
                run(repo=repo)
            claim = next(node for node in refreshed_graph["nodes"] if node["id"] ==
                         "urn:ghostmesh-readers:claim:fleet-activity-reported")
            source = json.loads((repo / "knowledge/v0.1/readers.source.json").read_text())
            self.assertEqual(next(node for node in source["nodes"] if node["id"] == claim["id"])
                             ["provenance"]["sourceFileSha256"], claim["provenance"]["sourceFileSha256"])
            cited_page.write_text(cited_page.read_text()[:-1])
            (repo / "site/knowledge/index.html").write_text("stale output")
            with self.assertRaisesRegex(ValueError, "stale generated output"):
                run(check=True, repo=repo)

    def test_private_classification_is_denied(self):
        self.invalid(lambda m: m["nodes"][1].__setitem__("visibility", "private"))
        self.invalid(lambda m: m["relationships"][0].__setitem__("visibility", "restricted"))

    def test_private_path_and_secret_in_public_field_are_denied(self):
        self.invalid(lambda m: m["nodes"][1].__setitem__("label", "/Users/owner/80-private/notes"))
        self.invalid(lambda m: m["nodes"][1].__setitem__("label", "ghp_abcdefghijklmnopqrstuv"))
        self.invalid(lambda m: m["nodes"][1].__setitem__("label", "github_pat_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
        self.invalid(lambda m: m["nodes"][1].__setitem__("label", "AKIAABCDEFGHIJKLMNOP"))
        self.invalid(lambda m: m["nodes"][1].__setitem__("label", "person@example.com"))

    def test_claim_must_match_published_quote_and_hash(self):
        self.invalid(lambda m: m["nodes"][1].__setitem__("statement", "Invented evidence"), "exact text")
        self.invalid(lambda m: m["nodes"][1]["provenance"].__setitem__("quoteSha256", "0" * 64), "quote hash")
        self.invalid(lambda m: m["nodes"][1]["provenance"].pop("quoteSha256"), "missing")
        self.invalid(lambda m: m["nodes"][1]["provenance"].__setitem__("locator", "#governance"), "source anchor")
        self.invalid(lambda m: m["nodes"][0]["source"].__setitem__("sha256", "0" * 64), "source hash")

    def test_external_content_is_not_certified_without_bytes(self):
        self.invalid(lambda m: m["nodes"][2].__setitem__("contentSha256", "0" * 64), "not in public custody")
        self.invalid(lambda m: m["nodes"][2].__setitem__("urlSha256", "0" * 64), "URL hash")
        self.invalid(lambda m: m["nodes"][2].__setitem__("url", "https://unrelated.example/report"), "URL hash")

    def test_citation_url_must_share_exact_claim_anchor(self):
        def cite_footer(model):
            url = "https://ghostmesh.ai/"
            model["nodes"][2]["url"] = url
            model["nodes"][2]["urlSha256"] = hashlib.sha256(url.encode()).hexdigest()
        self.invalid(cite_footer, "citation target absent from claim source anchor")

    def test_relationship_cannot_be_promoted_or_invented(self):
        self.invalid(lambda m: m["relationships"][0].__setitem__("authority", "admitted"))
        self.invalid(lambda m: m["relationships"][0].__setitem__("type", "governs"))
        self.invalid(lambda m: m["relationships"][0].__setitem__("to", m["nodes"][0]["id"]), "Claim-to-EvidenceSource")
        self.invalid(lambda m: m["relationships"][0]["provenance"].__setitem__("locator", "#governance"),
                     "provenance")

    def test_duplicate_and_wrong_namespace_are_denied(self):
        self.invalid(lambda m: m["nodes"].append(copy.deepcopy(m["nodes"][0])), "duplicate node")
        self.invalid(lambda m: m["nodes"][0].__setitem__("id", "urn:ghostmesh-readers:claim:wrong"),
                     "Reader ID namespace")

    def test_versioned_negative_fixtures_fail(self):
        cases = json.loads((ROOT / "knowledge/v0.1/fixtures/negative-cases.json").read_text())
        self.assertEqual(cases["fixtureVersion"], "0.1.0")
        for case in cases["cases"]:
            with self.subTest(case=case["name"]):
                model = copy.deepcopy(self.model)
                parts = case["pointer"].strip("/").split("/")
                target = model
                for part in parts[:-1]:
                    target = target[int(part)] if isinstance(target, list) else target[part]
                target[parts[-1]] = case["value"]
                with self.assertRaises(ValueError):
                    validate_contract(model, self.schema)

    def test_generated_outputs_and_manifest_are_reproducible(self):
        expected = run(check=True)
        manifest = json.loads(expected["site/knowledge/v0.1/publication-manifest.json"])
        linked = json.loads(expected["site/knowledge/v0.1/readers.jsonld"])
        discovery = json.loads(expected["site/.well-known/ghostmesh-knowledge.json"])
        self.assertEqual(linked["@context"]["sourceFileSha256"], "gm:sourceFileSha256")
        self.assertTrue(any(item.get("gm:nodeType") == "Claim" and "gm:provenance" in item
                            for item in linked["@graph"]))
        self.assertEqual(discovery["publicationMode"], "source-only")
        self.assertEqual(discovery["jsonld"],
                         "https://youtube.shareplane.malott.ai/knowledge/v0.1/readers.jsonld")
        self.assertEqual(discovery["scoutResearchRelationships"],
                         "https://youtube.shareplane.malott.ai/scout/research/relationships.json")
        self.assertEqual(manifest["outputsDigest"],
                         hashlib.sha256((json.dumps(manifest["outputs"], sort_keys=True,
                                                    ensure_ascii=False, separators=(",", ":")) + "\n").encode()).hexdigest())
        for entry in manifest["outputs"]:
            self.assertEqual(entry["sha256"], hashlib.sha256(expected[entry["path"]]).hexdigest())
            self.assertEqual(entry["bytes"], len(expected[entry["path"]]))
        page = expected["site/knowledge/index.html"].decode()
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        for reader in catalog["readers"]:
            with self.subTest(slug=reader["slug"]):
                self.assertIn(f'<h3><a href="/{reader["slug"]}/">', page)
                self.assertNotIn(f'<h3><a href="{catalog["host"]}/{reader["slug"]}/">', page)
        for node in self.model["nodes"]:
            if node["type"] == "Claim":
                slug = node["provenance"]["sourceNodeId"].removeprefix("urn:ghostmesh-readers:reader:")
                self.assertIn(f'href="/{slug}/{node["provenance"]["locator"]}"', page)
        self.assertNotIn('>Reader source</span>', page)
        self.assertIn('<span>Paper · arXiv</span>', page)
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            source_paths = [node["source"]["path"] for node in self.model["nodes"]
                            if node["type"] == "Reader"]
            for rel in ("knowledge/v0.1/readers.source.json", "knowledge/v0.1/contract.schema.json",
                        "content/catalog.json",
                        *source_paths):
                target = repo / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
            self.assertEqual(expected, run(repo=repo))
            run(check=True, repo=repo)
            file = repo / "site/knowledge/v0.1/readers.json"
            file.write_text(file.read_text() + " ")
            with self.assertRaisesRegex(ValueError, "stale generated output"):
                run(check=True, repo=repo)


if __name__ == "__main__":
    unittest.main()
