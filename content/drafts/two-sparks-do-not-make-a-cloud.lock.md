# Reader #67 Creative Lock | Tony approval November 17, 2026

**Authority:** Tony explicitly responded "Approved next" after the complete v0.2 manuscript, Reader #66 presentation direction, and three Reader + two SharePlane relationship recommendations were reported. This accepts the editorial/design package for mechanical implementation and draft UAT, **not** publication or exact-head merge. No new owner PREPARE gate.

## Identity and immutable editorial input
- Lane: GhostMesh YouTube Reader, deep source deconstruction.
- Issue: https://github.com/pinklon/ghostmesh-readers/issues/193
- Title: *Two Sparks Do Not Make a Cloud*.
- Subtitle: *Can $10,000 of local AI replace frontier coding agents? LinuxBTW's Minecraft experiment reveals why speed, quota freedom and correctness must be measured separately.*
- Slug and catalog id: `two-sparks-do-not-make-a-cloud` / `reader:two-sparks-do-not-make-a-cloud`.
- Target authored HTML: `content/readers/two-sparks-do-not-make-a-cloud.html`; published URL only after release: `https://youtube.shareplane.malott.ai/two-sparks-do-not-make-a-cloud/`.
- Approved full uncompressed public manuscript: `content/drafts/two-sparks-do-not-make-a-cloud.md` **as committed in `b8c9bab898175ecea7be1461770fafbe84e89d41`**, Git blob SHA `1cae8bbf00bfb8a9e923915337e9923b2a6a58f4`. Do not use the older editable issue comments as the authoritative bytes. Copy prose without semantic compression, embellishment, or invented specificity.
- Audience: engineers evaluating local inference, coding agents, model-serving capacity, and hybrid AI economics.
- Thesis: source's first-reported completion is not verified compliant completion. Two DGX Sparks increase local memory capacity and custody but do not by themselves establish cloud-model parity, agent reliability, comparable throughput or economic break-even.
- Section order: preserve the Markdown source sections in order: three-part brief; first-screen Assessment; actual Minecraft test and creator-reported matrix; memory/throughput explanation; workload ownership; falsifiable qualification test; economics; earned final Verdict; provenance and limits. Add opt-in player and chapter navigation without displacing or abridging authored copy.
- Required explanatory modules: four-contender comparison (reported times and initial functional compliance), dual distributed-memory versus one-GPU figure, compact falsification/acceptance rubric. No generic decorative hero, no fabricated benchmark chart.

## Source, claim posture and disclosure
- Primary source: LinuxBTW, *I Bought 2 NVIDIA DGX Sparks to Replace Cloud AI*, video `pAC1SRr1_Rc`, published September 8, 2026, 27:30. Chapters from source metadata, not independently listening-certified.
- Privately held automatic English-original timed captions: SHA-256 `eda5b04e8858018628672a2467d44dc97016c25ed600f8e134fc4104ae44f8f3`; automatic recognition can corrupt exact product/model names and is not audiovisual authentication. Never commit transcript, VTT, media, or private custody path.
- Maker sources: https://www.nvidia.com/en-us/products/workstations/dgx-spark/ and https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/ establish official device specs, not measured agent performance.
- Creator-reported times and first-pass outcomes remain attributed, non-normalized and not independently reproduced. Model families (Claude, Codex, Grok, local Qwen) deliberately remain generic; do not invent version labels or certify visual outcomes. If verifier finds a material contradiction, HOLD and return to Tony before altering copy.
- Technical editorial derivations: dense 70B raw BF16 weights ~140GB; FP8 raw weights ~70GB; 1792/273 ~6.56 nominal bandwidth ratio. These omit inference overhead, kernel constraints, context, and multi-node communication. Never present them as token/s measurements or a unified 256GB VRAM device.
- Public-safe boundary: disclose Tony-authorized Hyperion RTX PRO 6000 Blackwell 96GB comparison only; no internal endpoints, credentials, private data, employer/client references, or unpublished benchmark results.
- Verbatim limitation posture: preserve the public source/evidence note in the locked manuscript, including exact model-version uncertainty, creator attribution and no independent reproduced benchmark. No separate safety/legal disclaimer required.

## Presentation and interaction
- Primary visual baseline: published Reader #66, *Uncensored, Private, or Sovereign?*; centered ~740px reading measure, TOC in left gutter, aligned Related Thinking font, icon light/dark toggle, source-first cold-reader orientation, restrained headline and existing search/share chrome.
- Selective technical figure precedent: Reader #59. Diagram must show **two separate 128GB Spark memory domains connected by 200Gb/s interconnect**, versus **one local 96GB RTX PRO 6000 memory domain**. Show memory bandwidth only as maker nominal label, not inferred tok/s. Accessible text alternative mandatory.
- Comparison matrix must make creator-reported/non-normalized status visible. At 320/390/430px stack results or use genuinely legible responsive cards without horizontal reading burden.
- Existing click-to-load YouTube thumbnail/player and seek links; no eager iframe; external source fallback, keyboard navigation and focus indicators. Source-specific chapter labels must match video metadata and source claims.
- Existing Reader design system only. No new runtime framework, publisher, backend, image generation, theme machinery or site-wide restyle. Responsive dark/light and reading rail from accepted baseline.

## Approved editorial relationships
**Reader plane, companions only, not source corroboration:**
- `reader:the-12gb-gpu-has-a-three-budget-problem`: fit/bandwidth/context tradeoffs.
- `reader:uncensored-private-or-sovereign`: ownership/custody versus autonomy.
- `reader:the-grader-is-part-of-the-harness`: independent grading versus self-declared completion.
Review decision: linked, with distinct rationales above. Confirm exact current catalog IDs before mechanical insertion; do not substitute silently.

**SharePlane Work plane, independently labeled editorial comparisons, not video evidence:**
- Token Burn: `https://shareplane.malott.ai/tools/token-burn/` (dated rate/composition tool, not a Spark ROI oracle).
- Frontier Inference Without Frontier Custody: `https://shareplane.malott.ai/artifacts/frontier-inference-without-frontier-custody/` (custody architecture, not an empirical benchmark).
Review decision: linked, rationale above. Confirm canonical publication URLs are live before admission; report broken links, do not invent replacements.
- SharePlane-specific `dependsOn`, `supports`, `patternDependencies` and `site/artifact-graph.json`: **not applicable** to Reader repository; use existing Reader catalog/projection and relationships contract.

## Mechanical scope, validation and delivery
- Branch: `reader67-two-sparks` from current main (already created), one single draft PR to main. Existing source file and this lock file; implement one authored HTML, source map, one catalog record plus deterministic generated Reader site/index/knowledge projections, normal sanitized receipt, existing editorial-review/depth records once genuinely reviewed. No unrelated files or site-wide changes. Exact validator/receipt paths use existing Reader conventions.
- Read `docs/NEXT_READER.md`, `docs/READER_RELEASE_RUNBOOK.md`, actual catalog/schema, and repo instructions before implementation. Reconcile current GitHub state and owner work. Do not copy content from unverified local checkout.
- Use `make reader-prepare` for local projection/checks, existing focused tests and hosted CI. Validate exact-source claim map, catalog + both relationship layers, private-source exclusion, syntax, links/anchors and `git diff --check`. Run desktop plus 320/390/430px mobile browser UAT: first screen, TOC, source player, chapter seek, theme, no overflow, related cards and console health. Use existing Netlify preview, not another deployment system.
- Independent source/editorial/privacy acceptance on stable authored source bytes and aid digest is required via existing reviewer; do not fabricate PASS or add new reviewer machinery. Preview is not proof of public deployment.
- PR stays **draft, unmerged, automerge off**. Tony must explicitly authorize **publication of the reviewed candidate at exact head SHA** after preview UAT. No more routine owner approvals after that decision. If source/copy/design/material scope changes, return for the affected owner decision.
- Rollback before publication: close draft PR and leave production untouched. After publication: revert the scoped merge via normal protected workflow if necessary. Closeout must verify main merge SHA, production HTTP and real page markers, source privacy, Reader/SharePlane links, public receipt and catalog.
- Excluded: media/VTT/transcripts/private host paths, invented run-version labels, new public benchmark claims, extra orchestrators, new services, bulk past-Reader retrofits or unrequested publication.

**Gate decision:** Tony's approval locks the identified complete manuscript and the cited design/relationship decisions for a draft implementation. Outstanding exact model versions and visual-outcome details are deliberately UNKNOWN, not required publication claims. If mechanical execution reveals a contradictory link, schema or source fact, stop that affected change and report; otherwise advance the scoped PR to owner preview.

## November 17 owner-approved narrow amendment
Tony explicitly approved replacing the stale pre-lock verification sentence with: “Specific model names, settings, quantitative results and visual outcomes remain unverified and require cue-by-cue confirmation before they can be presented as established findings.” The amended manuscript is Git blob `2d5f5885d30e0c470657b16d9dd0ce474d986521`; this supersedes the original blob for that single sentence only. Tony also approved adding Grok's reported outcome to the unverified source claim register/map and restoring Token Burn's previously locked `/tools/token-burn/` URL. No wider rewrite, audiovisual verification, or independent benchmark claim is authorized.