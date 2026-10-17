# GhostMesh Readers

The public, video-first companion to [SharePlane](https://shareplane.malott.ai/). The Readers site is deliberately separate from SharePlane Production and private ReasonPack processing.

**Live collection:** https://youtube.shareplane.malott.ai/

**Netlify project:** `shareplane-youtube` (existing site ID: `27352ed6-0f74-4756-832e-95ba49e31b09`). **Publish directory:** `site/`, configured by `netlify.toml`; no dependency installation or build command.

## Add a Reader

1. Create `site/<slug>/index.html`. Show the original YouTube video with an opt-in player, a direct YouTube fallback, and selected timestamp links.
2. State GhostMesh's verdict near the top: who should watch, what to skip or verify, and what to do next. Ground the call in this video's strongest and weakest evidence. Distinguish a speaker's experience from a measured result and GhostMesh's inference from either.
3. Publish original editorial analysis, source-video timestamps, and a sanitized machine-readable `receipt.json` with claim-level provenance and evidence hashes. Retain original media, source captions, and transcripts only in an access-controlled private ReasonPack. Never copy or commit third-party transcript, caption, or media files into `site/`, even if no page links to them. Receipt metadata must omit signed stream URLs, credentials, private paths, and nonpublic details.
4. Update the collection in `site/index.html` and `site/sitemap.xml`; keep all existing slugs.
5. Run `python3 scripts/check_site.py` and inspect desktop and narrow-screen layouts before publication. GitHub Actions verifies pull requests and pushes.
6. Review the proposed change, merge into `main` only after verifying private ReasonPack custody, and check the Netlify deployment. Confirm the source video, editorial analysis, and receipt load while the former public transcript and captions return unavailable responses.

## Hosting separation

The public site is immutable, static Git content. Mac Studio, Hyperion and the GhostMesh VPS can propose new content but none is required to keep the site available. Each production deployment must be traceable to a Git commit. Do not publish private media packs, email addresses, credentials, machine paths, private agent histories, or nonpublic SharePlane Works.

## Hosting connection

The existing Netlify project `shareplane-youtube` is connected to GitHub repository `pinklon/ghostmesh-readers`, production branch `main`. Keep `site/` as the publish directory, with no build command. Do not create another Netlify project or modify Cloudflare DNS. The live domain is `youtube.shareplane.malott.ai`.

## Recovery

Restore a previous successful Netlify deploy, or revert a publication commit. Do not force push or delete the public history as a routine rollback.

## Public evidence boundary

The site and repository are public. No third-party video, audio, full transcript, subtitle, or caption artifact belongs in their current source trees, including unlinked files. Publish source links, bounded quotations when warranted, independently authored criticism, and sanitized receipts instead. Keep source artifacts private and hash-verifiable. Deleting a file from the current tree does **not** erase it from Git history or historical Netlify deploy URLs; address historical exposure separately, without force-pushing or destroying private evidence.
