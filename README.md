# GhostMesh Readers

The public, video-first companion to [SharePlane](https://shareplane.malott.ai/). The Readers site is deliberately separate from SharePlane Production and private ReasonPack processing.

**Live collection:** https://youtube.shareplane.malott.ai/

**Netlify project:** `shareplane-youtube` (existing site ID: `27352ed6-0f74-4756-832e-95ba49e31b09`). **Publish directory:** `site/`, configured by `netlify.toml`; no dependency installation or build command.

## Add a Reader

1. Create `site/<slug>/index.html`. Show the original supported video with an opt-in player and a direct source fallback. Use timestamp links where the platform supports them; otherwise label source timings without promising a seek.
2. Put the three-part [Reader brief](#canonical-reader-brief) near the top, before the long analysis: what the video is about, why the intended reader should care, and what GhostMesh takes away. Follow it with a verdict that says who should watch, what to watch or skip, what to verify, and what to do next. Ground the call in this video's strongest and weakest evidence. Distinguish a speaker's experience from a measured result and GhostMesh's inference from either.
3. Publish original editorial analysis, source-video timestamps, and a sanitized machine-readable `receipt.json` with claim-level provenance and evidence hashes. Retain original media, source captions, and transcripts only in an access-controlled private ReasonPack. Never copy or commit third-party transcript, caption, or media files into `site/`, even if no page links to them. Receipt metadata must omit signed stream URLs, credentials, private paths, and nonpublic details.
4. Update the collection in `site/index.html` and `site/sitemap.xml`; keep all existing slugs.
5. Run `python3 scripts/check_site.py` and inspect desktop and narrow-screen layouts before publication. GitHub Actions verifies pull requests and pushes.
6. Review the proposed change, merge into `main` only after verifying private ReasonPack custody, and check the Netlify deployment. Confirm the source video, editorial analysis, and receipt load while the former public transcript and captions return unavailable responses.

## Canonical Reader brief

Every future publication must answer these three questions plainly and visibly near the top of the Reader, before the source route, evidence ledger, or detailed critique. Use the questions as headings or equally clear labels; do not make readers infer the answers from a thesis or claim audit.

1. **What is the video about?** Give a short, accessible overview of its subject, speaker, main argument or demonstration, and what happens in the video. State the video's story before evaluating it.
2. **Why should a reader care?** Name the audience and the practical decision, risk, opportunity, or useful idea the video raises. Say when it is worth watching and when a reader can reasonably skip it.
3. **What does GhostMesh take away?** State GhostMesh's own conclusion and its practical consequence: an action, bounded experiment, design rule, or reason to hold judgment. Tie it to the source evidence and label inference. A generic recap or a restatement of the speaker's pitch does not satisfy this item.

The near-top verdict should turn the brief into a recommendation: useful source timestamps, sections to skip or verify, and a next step. Keep claim-level scrutiny and custody details below this reader orientation. Include matching `overview`, `whyItMatters`, and `ghostMeshTakeaway` fields in the sanitized receipt so the public editorial intent is inspectable alongside the claim map. `scripts/check_site.py` enforces the visible brief and matching receipt fields for new Readers; earlier editions are grandfathered. During review, read the brief on its own; a reader should understand the video, its relevance, and GhostMesh's conclusion without needing the evidence ledger.

## Hosting separation

The public site is immutable, static Git content. Mac Studio, Hyperion and the GhostMesh VPS can propose new content but none is required to keep the site available. Each production deployment must be traceable to a Git commit. Do not publish private media packs, email addresses, credentials, machine paths, private agent histories, or nonpublic SharePlane Works.

## Hosting connection

The existing Netlify project `shareplane-youtube` is connected to GitHub repository `pinklon/ghostmesh-readers`, production branch `main`. Keep `site/` as the publish directory, with no build command. Do not create another Netlify project or modify Cloudflare DNS. The live domain is `youtube.shareplane.malott.ai`.

## Recovery

Restore a previous successful Netlify deploy, or revert a publication commit. Do not force push or delete the public history as a routine rollback.

## Public evidence boundary

The site and repository are public. No third-party video, audio, full transcript, subtitle, or caption artifact belongs in their current source trees, including unlinked files. Publish source links, bounded quotations when warranted, independently authored criticism, and sanitized receipts instead. Keep source artifacts private and hash-verifiable. Deleting a file from the current tree does **not** erase it from Git history or historical Netlify deploy URLs; address historical exposure separately, without force-pushing or destroying private evidence.
