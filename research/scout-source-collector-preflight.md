# Scout source-collector trial: external retrieval preflight

Status: **PARTIAL**, research-only. Date: 2026-10-22.
This is an externally inspected source preflight, **not** execution of `scout_source_collector.py` or independently hashed snapshots.

## Three observed sources

1. https://arxiv.org/abs/2601.19921
   - Public HTML abstract retrieved using an external reading interface.
   - Source identifies the multi-agent debate study and its confidence/diversity interventions.
   - Primary evidence: authors' abstract, **not** an independently replicated result.
   - Proposed connection: test whether diverse initial evidence beats more agents sharing the same evidence.

2. https://arxiv.org/abs/2606.09840
   - Public HTML abstract retrieved using an external reading interface.
   - Source is a conceptual position paper on multi-human/multi-agent sensemaking, provenance, and authorship.
   - Proposed connection: preserve distinct human and agent contributions in GhostMesh/Readers.
   - Limitation: conceptual design is not a measured implementation outcome.

3. https://raw.githubusercontent.com/python/cpython/main/README.rst
   - Public text retrieved using an external reading interface.
   - This is a **negative control**: authoritative, useful software documentation but no specific Scout collaboration thesis justified.
   - The `main` branch is mutable; pin a commit before evidence hashing or repeatability claims.

## Collector trial limitations and acceptance gate

The local execution environment could not resolve github.com for direct checkout; the collector itself was **not run against these three URLs**. No response hashes, HTTP headers, bytes, or verified timestamps from the collector exist. Do not mark the collector live-tested.

The collector allows arxiv.org and raw.githubusercontent.com but currently returns raw HTML as an excerpt. It does not extract an article's abstract or separate navigation from substantive content. It also does not pin mutable URLs, record response ETag/Last-Modified, or compare sources semantically. The collector may therefore be network-functional yet insufficient for evidence-backed Connection Theses.

Next qualification: run the exact branch collector in a network-enabled isolated runner against these three URLs, record bytes/hash/response type, test an unreachable host and redirect, and inspect whether the captured excerpt contains enough relevant text. Do not publish or infer semantic accuracy from successful retrieval.
