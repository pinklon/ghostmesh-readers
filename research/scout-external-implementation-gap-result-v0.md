# Scout external capability comparison | Research result

Private editorial research, 2026-10-23. No deployment, privileged connector changes, or outreach.

## Bottleneck

Implementation evidence: https://github.com/areibman/bottleneck, default-branch README and package metadata inspected.

Documented capabilities: GitHub PR/diff browser, Electron desktop UI, incremental sync with local cached data, grouping, bulk PR actions, and keyboard-first review. GitHub repository metadata shows non-archived source with default branch master. Its README's performance figures are product targets, not validated benchmarks.

Scout's current research pipeline already tracks source provenance, review dispositions, claim-impact revisions, and private comparison views. It does **not** establish the real operator workflow Bottleneck targets: reviewing many simultaneous code changes quickly. Thus a useful review-speed comparison requires *sanitized PR queue and reviewer tasks*, which have not been collected or timed. A review client must not inherit production merge authority.

**Disposition:** investigate read-only review UX fixtures, not adopt software.

## InspectorRAGet

Implementation evidence: https://github.com/IBM/InspectorRAGet, README current as inspected 2026-10-23. It documents structured JSON evaluation data with metadata, models, metrics, documents, tasks and results. Task types include QA, RAG, tool calls and agentic tasks. It supports task-level inspection alongside aggregate metrics. The 2024 research paper https://arxiv.org/abs/2404.17347v2 is a related but older source, and should not be treated as a perfect description of the current repository.

A deterministic six-case Scout mapping exercise generated only *task skeletons*, not a valid full InspectorRAGet import. Two Scout fields map plainly into generic task inputs and text targets: `ghostmesh_problem`, `work_basis`. Eight other fields require deliberate representation: `source_url`, `source_kind`, `source_status`, `complementarity`, `counterevidence`, `experiment`, `disposition`, `review_status`.

This is a gap in the **initial straightforward mapping**, not proof that the external application cannot represent the fields with more work. The skeleton's text targets are evidence excerpts, not independently verified ground-truth answers.

**Disposition:** investigate evidence grammar and annotations with a six-case side-by-side review, not install or migrate systems.

## Surprise and transfer

Bottleneck's potentially transferable contribution is *fast human review of parallel agent work*. InspectorRAGet's is *traceable evaluation inspection*. Their value to GhostMesh depends on whether existing UI already serves those needs. Source-linked counterevidence and authority distinctions must not vanish when borrowing ideas.

Research files: `research/scout-external-capability-comparison-v0.json` (documented comparison), `scripts/scout_external_schema_gap.py` (auditor), VPS `/tmp/scout-trial-34Lfv9/scout-external-schema-gap-v0.json` (six-case result). Tests run under Scout suite and pass. No external application was installed, built or run.
