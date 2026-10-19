# GhostMesh Readers

The public, video-first companion to [SharePlane](https://shareplane.malott.ai/). The Readers site is deliberately separate from SharePlane Production and private ReasonPack processing.

**Live collection:** https://youtube.shareplane.malott.ai/

**Netlify project:** `shareplane-youtube` (existing site ID: `27352ed6-0f74-4756-832e-95ba49e31b09`). **Publish directory:** `site/`, configured by `netlify.toml`; no dependency installation or build command.

## Add a Reader

1. Create `content/readers/<slug>.html` with the five generation slots shown in existing templates, and add the catalog record. Show the original supported video with an opt-in player and a direct source fallback. Use timestamp links where the platform supports them; otherwise label source timings without promising a seek.
2. Put the three-part [Reader brief](#canonical-reader-brief) near the top, before the long analysis: what the video is about, why the intended reader should care, and what GhostMesh takes away. Follow it with a verdict that says who should watch, what to watch or skip, what to verify, and what to do next. Ground the call in this video's strongest and weakest evidence. Distinguish a speaker's experience from a measured result and GhostMesh's inference from either.
3. Publish original editorial analysis, source-video timestamps, and a sanitized machine-readable `receipt.json` with claim-level provenance and evidence hashes. Retain original media, source captions, and transcripts only in an access-controlled private ReasonPack. Never copy or commit third-party transcript, caption, or media files into `site/`, even if no page links to them. Receipt metadata must omit signed stream URLs, credentials, private paths, and nonpublic details.
4. Update `content/catalog.json` and the Reader template, then run `python3 scripts/generate_site.py`; keep all existing slugs.
5. Run `python3 scripts/check_site.py` and inspect desktop and narrow-screen layouts before publication. GitHub Actions verifies pull requests and pushes.
6. Review the proposed change, merge into `main` only after verifying private ReasonPack custody, and check the Netlify deployment. Confirm the source video, editorial analysis, and receipt load while the former public transcript and captions return unavailable responses.

## Canonical Reader brief

Every future publication must answer these three questions plainly and visibly near the top of the Reader, before the source route, evidence ledger, or detailed critique. Use the questions as headings or equally clear labels; do not make readers infer the answers from a thesis or claim audit.

1. **What is the video about?** Give a short, accessible overview of its subject, speaker, main argument or demonstration, and what happens in the video. State the video's story before evaluating it.
2. **Why should a reader care?** Name the audience and the practical decision, risk, opportunity, or useful idea the video raises. Say when it is worth watching and when a reader can reasonably skip it.
3. **What does GhostMesh take away?** State GhostMesh's own conclusion and its practical consequence: an action, bounded experiment, design rule, or reason to hold judgment. Tie it to the source evidence and label inference. A generic recap or a restatement of the speaker's pitch does not satisfy this item.

The near-top verdict should turn the brief into a recommendation: useful source timestamps, sections to skip or verify, and a next step. Keep claim-level scrutiny and custody details below this reader orientation. Include matching `overview`, `whyItMatters`, and `ghostMeshTakeaway` fields in the sanitized receipt so the public editorial intent is inspectable alongside the claim map. `scripts/check_site.py` enforces the visible brief and matching receipt fields for every Reader, including migrated editions. During review, read the brief on its own; a reader should understand the video, its relevance, and GhostMesh's conclusion without needing the evidence ledger.

## Hosting separation

The public site is immutable, static Git content. Mac Studio, Hyperion and the GhostMesh VPS can propose new content but none is required to keep the site available. Each production deployment must be traceable to a Git commit. Do not publish private media packs, email addresses, credentials, machine paths, private agent histories, or nonpublic SharePlane Works.

## Hosting connection

The existing Netlify project `shareplane-youtube` is connected to GitHub repository `pinklon/ghostmesh-readers`, production branch `main`. Keep `site/` as the publish directory, with no build command. Do not create another Netlify project or modify Cloudflare DNS. The live domain is `youtube.shareplane.malott.ai`.

## Recovery

Restore a previous successful Netlify deploy, or revert a publication commit. Do not force push or delete the public history as a routine rollback.

## Public evidence boundary

The site and repository are public. No third-party video, audio, full transcript, subtitle, or caption artifact belongs in their current source trees, including unlinked files. Publish source links, bounded quotations when warranted, independently authored criticism, and sanitized receipts instead. Keep source artifacts private and hash-verifiable. Deleting a file from the current tree does **not** erase it from Git history or historical Netlify deploy URLs; address historical exposure separately, without force-pushing or destroying private evidence.

## Normalized publishing contract (Issue 23)

All 13 existing Readers and future editions now use the same structural gate. There are no grandfather exceptions. `content/catalog.json` is the authoring authority for identity, brief, classification, source metadata, claim inventory, references, relationships, editorial ordering, theme variant and revision history. `content/readers/<slug>.html` retains the original analysis and source controls, with bounded generation slots. Edit these inputs, then run:

```sh
python3 scripts/generate_site.py
python3 scripts/check_site.py
python3 -m unittest discover -s tests -v
```

Commit both inputs and generated `site/` files. Hosting still serves `site/` directly with no package installation or build command. CI rejects drift. The declarative schema is `content/catalog.schema.json`; the standard-library checker additionally enforces cross-record identities, references, timestamps, privacy, all existing routes, sitemap, bounded homepage and the complete non-JavaScript archive.

The homepage has one manifest-selected feature and six compact cards. `/readers/` provides text search, category and tag intersection, latest-first, title and authored editorial-order sorting. Six static category routes work without JavaScript. Empty categories explicitly say that no Reader is classified there. No graph admission into SharePlane, Tony Brain or Library Atlas is implied by these local public reading routes.

Reader source players share one generated aspect contract. `source.mediaAspect` records the intrinsic shape: `16:9`, `9:16`, `1:1`, or `unknown`. The current 12 landscape videos and one portrait Reel were checked against read-only public metadata in [the aspect evidence table](docs/PLAYER_ASPECT_EVIDENCE.md). The generator refuses to embed a source with an unknown aspect; that source stays link-only until dimensions are checked. The visual frame is wide by default, while a portrait or square frame has a centered width limit. All embeds remain opt-in, with external source links and original timestamp controls. `tests/player_regressions.cjs` renders all 13 pages at desktop/mobile widths plus synthetic landscape, portrait and square fixtures using local Chrome; no media download is needed.

`/knowledge/` is a versioned, source-only public projection. It identifies all 13 Reader pages and includes one claim and citation checked against exact published Reader text. This is not a graph admission or a certification of factual truth. The source, schema, and fixtures live in `knowledge/v0.1/`; `scripts/knowledge_contract.py` regenerates seven deterministic static outputs. After editing any Reader page, run `python3 scripts/generate_site.py` and update the pinned public source hash only after reviewing the claim text, anchor and source URL. Then run `python3 scripts/knowledge_contract.py`, both generators with `--check`, the site checker and all tests. `ARCHITECTURE.md` and `INTEGRATION_PLAN.md` describe the contract and inactive downstream adapters.

Every Reader carries the three-question brief before its source player, explicit recommendation and proposed architecture impact, dated corroboration/counterevidence register, sanitized receipt and qualified related-thinking disposition. Historical analysis and source-custody statements retain their original scope. A new receipt for an older page does not assert a fresh private-pack verification. An unverified claim is not silently promoted because another paragraph has a source. Vendor primary documentation supports documented statements, not independent performance confirmation. Reference dates distinguish publication, last file update and unknown measurement dates; sources sharing an evidence family are not independent replications.

Preserve claim IDs when revising a proposition and record the reason and time in `revisionHistory`. Material conclusion changes need source-backed editorial revision. Recheck mutable incident and product claims before operational use. Do not infer current service state from historical GhostMesh operational descriptions. No recurring crawling or paid service is enabled. Automated checks cannot certify citation entailment, independence, reputation, completeness or currency: independent editorial review remains required.

No U+2014 character is allowed in authored rendered prose, metadata, public receipt display strings or generated text. The generator rejects it in catalog strings; the checker decodes HTML entities and checks rendered text and metadata. If an exact attributed quotation needs the character, do not silently rewrite it: revise the publication design or obtain an explicit, reviewable exception. This migration found no such quoted-character exception to retain. Historical before-state audit data is preserved separately from rendered publication copy.

Themes open in the established dark GhostMesh appearance and offer local `system`, `light` and `dark` preferences, with no external service. No-JavaScript Reader pages follow the system scheme; the homepage keeps its dark visual grammar. Three scoped visual variants (`fieldnotes`, `dossier`, `essay`) and three adaptive accent palettes keep the evidence hierarchy consistent while varying composition and typography. `tones.css` maps legacy colors; `knowledge.css` isolates new components. Validate at 390px and desktop in both schemes, with keyboard, reduced motion, blocked local storage, no-JavaScript and opt-in playback checks whenever changing theme or source controls.

The normalization PR is source-only. Automatic Netlify PR preview is owner-authorized for this tranche; merging, production deployment, infrastructure and credentials remain outside scope. Review source and evidence before any separate promotion decision.
