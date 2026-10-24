# Scout cross-source review: Bottleneck and InspectorRAGet

Research-only editorial assessment, 2026-10-23. These are two public source-work candidates, not verified collaboration partners, and no source author or repository contributor has expressed interest in GhostMesh.

## Bottleneck: agent-native PR review

Source implementation: https://github.com/areibman/bottleneck (GitHub default branch `master`). Repository README and current GitHub repository metadata inspected on 2026-10-23.

Observed implementation: Electron desktop app using React, Monaco, SQLite local cache, GitHub API/GraphQL incremental sync, fast diff navigation, PR grouping, bulk actions, offline access and power-user keyboard shortcuts. The README discusses parallel background agents and concurrent threads; it includes explicit performance targets, which **are targets, not independent benchmark measurements**. The README identifies a PR interface, not a GhostMesh agent orchestrator or trust enforcement plane. Public repository metadata showed a last source push of 2025-12-04; this timestamp may differ from tagged releases.

Unexpected connection: a product targeted at reviewing many simultaneous agent-generated PRs could illuminate GhostMesh's review bottleneck. The connection is operational interaction design, not an autonomous reviewer. A GitHub account seen contributing to another project publicly owns this repository. Same account is not verified personal identity and does not imply its owner wants to collaborate.

Strongest objection: GhostMesh's pain also includes source custody, approval loops, and release authority. Faster batch review alone can speed up the *wrong* action. Bulk merge/close and OAuth represent permissions that require separate governance. Installing this app is neither necessary nor approved.

Decisive private test: use existing **sanitized** GhostMesh PR metadata and read-only diff fixtures to compare current review workflow with a Bottleneck-inspired grouped queue. Measure time to find review blockers, erroneous approval intent and reviewer context switching. Do not connect privileged GitHub credentials or install software in the owner's existing workflow.

Disposition: **INVESTIGATE USER EXPERIENCE**. Originality, claims of speed and real operator value remain unverified.

## InspectorRAGet: evaluation inspection as an artifact

Research paper: https://arxiv.org/abs/2404.17347v2
Open code: https://github.com/IBM/InspectorRAGet

The published research describes aggregate and instance-level evaluation, combining human and algorithmic judgments and annotator quality. The **currently available open repository** provides React/Next.js inspection of JSON evaluation data, including metadata, models, metrics, documents, tasks and results, task contexts, targets, evaluator annotations, and agentic tool-call trajectories. Its README names converters for BFCL tool calling and agentic benchmarks. The repository default-branch README was inspected on 2026-10-23; current implementation may be newer than the 2025 research paper.

Unexpected connection: Scout's evidence and model-evaluation conclusions could become inspectable task-level artifacts rather than disconnected quality scores. This is a concrete schema and user interface pattern: show raw context, output, provenance, human disagreement, system metrics and corrections side by side.

Strongest objection: InspectorRAGet is designed for completed evaluation datasets. Scout discovery claims, changing web sources and author-attribution uncertainty require different semantics and live revision edges. Current Scout workspace already has history and claim-impact views, so duplicating another entire application risks pointless machinery.

Decisive private test: map a **six-case sanitized** Scout research fixture to InspectorRAGet's documented schema, enumerate fields that survive or are lost (source revision, counterevidence, dissent, uncertain identity, review authority), and compare human error-finding against the existing Scout view. No deployment or direct integration required.

Disposition: **INVESTIGATE EVIDENCE GRAMMAR**, not an adoption decision.

## Comparative hypothesis

Bottleneck emphasizes throughput of *reviewing actions*; InspectorRAGet emphasizes inspection of *evaluation evidence*. GhostMesh needs both capacities but must not confuse faster navigation with authorization or more charts with reproducibility. A structured source/counterargument/decision comparison is a more discriminating next experiment than contacting either source's contributors.

No public publication, external outreach, install, production merge or model authority is authorized.
