# Scout #76 reproduction source-stage receipt

Date: November 6, 2026 Pacific
Issue: https://github.com/pinklon/ghostmesh-readers/issues/76
Branch: `segfault/scout76-repro-companion-draft-20261106`
Base: `main` at `7320fd0ff331936c42c1d66124c30145160bbb89`
Status: SOURCE PACKAGE IMPLEMENTED AND LOCALLY TESTED. NO PUBLIC PAGE, NETLIFY PREVIEW OR RELEASE.

## Inputs and fidelity

- Tony-accepted manuscript frozen at `content/scout/publication-drafts/24-the-plateau-that-lied-reproducing-the-experiment.md` with SHA-256 `b4523498d768858afd60b7f59a400ed35e5a6e871593d069c9f42c3e9221da07`.
- Original attachment SHA-256 `f8f62a9d03ba75536ba73cdc79800201719e03623621d2205f5c269f7a9280fc`; only a terminal newline was added in the repository copy.
- Three pinned research definitions copied from Git commit `d46047390869ff372aa6239053ef882bd1b60a65`, with their original Git blob IDs validated at runtime.
- One dependency-free runner emits full synthetic `search.json`, `stopping.json`, `probe.json` and a manifest into a new caller-chosen directory, refuses overwrite, and checks expected summaries before writing.
- Source fixture mutation fails expected-value validation. No model or service calls exist in the runner.

## Focused local acceptance

- Python: `3.12.14`.
- `python3 -B -m unittest discover -s repro/scout-stopping -p 'test_reproduction.py' -v`: 4 PASS.
- `python3 -B -m py_compile repro/scout-stopping/run_reproduction.py repro/scout-stopping/test_reproduction.py`: PASS.
- `git diff --check`: PASS.
- Single real runner invocation to a fresh temporary directory: PASS. Row counts: search 432, stopping 240, probe 240.
- Output SHA-256: `search.json` `a132cc402c47e562b55f8b1913b64377118bd91ecd25788a331f24e7c8b9f9ee`; `stopping.json` `0cdc7b3ee7c92986525de8164f355c70e7d9aeefb3a7703ab1a1829e3c8f6972`; `probe.json` `b9eae67046b56899159175adb380b16ef5eb4c1cc80e50f9fcf1f833c365b84f`.
- Deterministic repeat and output hash verification: PASS in focused test.
- Synthetic output fields only; no private datasets or participant material included.

## Still outstanding

- Repository-wide `scripts/check_site.py` result, CI, GitHub draft PR head, Netlify preview, mobile/desktop review, and owner acceptance: NOT YET RECORDED.
- Public site route, index/RSS update and public package download: NOT IMPLEMENTED.
- Original raw archive reconciliation: UNKNOWN; independently reimplemented replication: NOT ESTABLISHED.
- Source manuscript's future-tense package status requires a focused editorial amendment before eventual publication; no rewrite is authorized here.
- Exact-head merge and Production deployment: NOT AUTHORIZED.

Rollback: drop the unmerged branch; Production remains unchanged. The two pre-existing dirty local worktrees were not modified.
