# Reader #59 Creative Lock Candidate | November 13, 2026

Status: editorial content accepted in direction by Tony; consolidated v0.4 manuscript is an immutable **draft candidate** for first implementation/preview, not authorization to publish. Tony's previous corrections are mandatory: no verdict spoilers up front, preserve source-first technical prose, include GhostMesh operational application only after evidence, no old SharePlane links, all evidence and 3+1 relationships.

## Identity and authority
- Lane: GhostMesh YouTube Reader, deep deconstruction.
- Canonical issue: https://github.com/pinklon/ghostmesh-readers/issues/166
- Source: Cloud Codes, *Is 12GB of VRAM Enough for Local AI Now?*, video `r2KBVvh_8Do`, 15:52.
- Title: *The 12 GB GPU Has a Three-Budget Problem*.
- Subtitle: *Running a 27-billion-parameter model locally is possible. Buying its advertised speed and context at the same time is a different proposition.*
- Slug/id: `the-12gb-gpu-has-a-three-budget-problem` / `reader:the-12gb-gpu-has-a-three-budget-problem`.
- Audience: local-AI users, hardware buyers, model and inference-service engineers.
- Approved editorial candidate, entire uncompressed text: `content/drafts/the-12gb-gpu-has-a-three-budget-problem.md`, SHA256 `fa538ba1230d01e3d59406bd74b9229489203dcfc5f01408116cc7d9560e0396`.
- Target authored article: `content/readers/the-12gb-gpu-has-a-three-budget-problem.html`, published path only after release `/the-12gb-gpu-has-a-three-budget-problem/`.
- Strongest mechanical reference: Reader #55; source-first opening: #57; concise assessment then earned end verdict: #58; preserve two-column responsive chrome.

## Locked argument and presentation
- Thesis: three independent feasibility budgets are weights, KV cache, and effective bandwidth; maximum context and peak tok/s from unlike experiments cannot be summed into a one-card promise; task-level quality and operating fit decide deployment.
- Public copy/section order: exact Markdown above, with opening, a *non-spoiler* two-sentence GhostMesh assessment, three-question scan, opt-in video and cue navigation, full technical deconstruction, GhostMesh implication, bounded qualification, final verdict, source/claim limitations, Reader comparisons, separately labeled SharePlane comparison. Convert Markdown mechanically to existing Reader HTML modules without compressing/rephrasing claims.
- Visuals: reuse existing Reader chrome and shared assets. No generated images, no hero nature imagery, no separate pattern registry, no new services or scripts unless existing generator requires a focused projection fix.
- Responsive acceptance: 320/390/430px and desktop, no overflow/overlap, player opt-in and seek links functional, readability and theme intact. Check actual rendered first screen for spoiler regression.

## Evidence/claim contract
- Maker architecture: https://huggingface.co/Qwen/Qwen3.8-27B ; https://github.com/QwenLM/Qwen3.8
- Quantization distribution and revision-sensitive file sizes: https://huggingface.co/unsloth/Qwen3.8-27B-GGUF
- Self-reported 3060 96K ~9.7 tok/s: https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/61
- Self-reported 3080 10GB 16K 64.4 tok/s and 32K spill reversal: https://github.com/sudoingX/qwen38-mtp
- Upstream MTP implementation, Qwen3.6-specific speed and memory: https://github.com/ggml-org/llama.cpp/pull/22673
- Pooled multi-card 262K example: https://github.com/bytefjord/qwen3.8-27b-dual-3060-12gb-llama.cpp
- Counterevidence MTP slower than standard decode on dual 3060: https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/77
- Video interpretation source: https://www.youtube.com/watch?v=r2KBVvh_8Do
- Cache arithmetic is editorial derivation and backend-dependent, not observed total VRAM. Community measurements not independent GhostMesh replications. Negative empirical claim bounded to located audited records. No assertion of universal impossibility. Cue metadata are navigation aids, not listening-certified.

## Relationships, editorial comparisons only
- Reader `reader:the-model-fits-does-the-intelligence-survive`: companion, compression and fitted weights do not prove task quality.
- Reader `reader:the-operator-is-part-of-the-denominator`: companion, real service and workload denominator rather than peak token rate.
- Reader `reader:the-engine-is-not-the-service`: related topic, decoding throughput is not the whole operational service.
- SharePlane Work: *The Most Expensive Model Is Often Compensation for Missing Control*, `https://shareplane.malott.ai/artifacts/the-most-expensive-model-is-often-compensation-for-missing-control/`: companion, model/compute upgrade can mask system design or workload-scope defects. This destination was found in current public catalog. Keep distinct from source evidence. The old *Right Model/Eval* heritage-redirected URL is excluded.

## Repo and privacy boundaries
- Allowed on a draft branch: one authored article, its source map/claim records, one catalog record, deterministic generated page/index projections, existing review/depth record after independent findings, focused existing tests and this editorial lock candidate.
- Forbidden: public media, raw transcripts, captions, local private-source directories, credentials, confidential hardware telemetry, unrelated Reader rewrites, new orchestrator, second publisher, registry-wide remodeling, autopublish.
- Private source verified by existing ReasonPack manifest and SHA256SUMS on governed host; not a Git artifact. Do not claim independent listening.
- Public-safe prose can describe GhostMesh methodology and hypothetical application, not live private endpoints or internal secrets.

## Validation, review and release
- Follow `docs/READER_RELEASE_RUNBOOK.md` v2 as current authority: first-candidate preflight, full-copy preservation, source/claim/cue links, 3+1 relationship records with review disposition, existing unit/local site/CI, desktop+narrow preview, independent editorial/source/privacy review on exact bound bytes.
- Initial PR: draft only, no auto-merge. The review receipt must say PENDING until actually accepted. Tony's semantic/UAT decision and later explicit **publish** decision govern normal exact-head protected merge and production release. No inference of publication authorization from “Next”.
- No new machinery. Rollback is closing/reverting the draft PR; production unchanged.
