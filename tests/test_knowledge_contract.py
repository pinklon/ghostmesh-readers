import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from sys import path as sys_path
sys_path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from knowledge_contract import ROOT, SCHEMA, SOURCE, run, validate_contract


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
        self.assertEqual(len(self.model["nodes"]), len(catalog["readers"]) + 2)
        self.assertEqual(len(self.model["relationships"]), 1)
        self.invalid(lambda m: m["nodes"].pop(), "Reader inventory")

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
        self.assertEqual(manifest["outputsDigest"],
                         hashlib.sha256((json.dumps(manifest["outputs"], sort_keys=True,
                                                    ensure_ascii=False, separators=(",", ":")) + "\n").encode()).hexdigest())
        for entry in manifest["outputs"]:
            self.assertEqual(entry["sha256"], hashlib.sha256(expected[entry["path"]]).hexdigest())
            self.assertEqual(entry["bytes"], len(expected[entry["path"]]))
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
