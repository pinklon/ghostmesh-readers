# GhostMesh Readers

The public, video-first companion to [SharePlane](https://shareplane.malott.ai/). The Readers site is deliberately separate from SharePlane Production and private ReasonPack processing.

**Live collection:** https://youtube.shareplane.malott.ai/

**Netlify project:** `shareplane-youtube` (existing site ID: `27352ed6-0f74-4756-832e-95ba49e31b09`). **Publish directory:** `site/`, configured by `netlify.toml`; no dependency installation or build command.

## Add a Reader

1. Create `site/<slug>/index.html`. Show the original YouTube video with an opt-in player, a direct YouTube fallback, and selected timestamp links.
2. State GhostMesh's verdict near the top: who should watch, what to skip or verify, and what to do next. Ground the call in this video's strongest and weakest evidence. Distinguish a speaker's experience from a measured result and GhostMesh's inference from either.
3. Publish a UTF-8 timed transcript, the preserved source-caption VTT when available, a machine-readable `receipt.json` with a timestamped claim map and provenance, and `SHA256SUMS.txt` for those public files. Mark automatic captions as uncorrected. The receipt must omit signed stream URLs, credentials, private paths, and nonpublic details; media stays in the local ReasonPack.
4. Update the collection in `site/index.html` and `site/sitemap.xml`; keep all existing slugs.
5. Run `python3 scripts/check_site.py` and inspect desktop and narrow-screen layouts before publication. GitHub Actions verifies pull requests and pushes.
6. Review the proposed change, merge into `main`, and check the Netlify deployment and public downloads.

## Hosting separation

The public site is immutable, static Git content. Mac Studio, Hyperion and the GhostMesh VPS can propose new content but none is required to keep the site available. Each production deployment must be traceable to a Git commit. Do not publish private media packs, email addresses, credentials, machine paths, private agent histories, or nonpublic SharePlane Works.

## Hosting connection

The existing Netlify project `shareplane-youtube` is connected to GitHub repository `pinklon/ghostmesh-readers`, production branch `main`. Keep `site/` as the publish directory, with no build command. Do not create another Netlify project or modify Cloudflare DNS. The live domain is `youtube.shareplane.malott.ai`.

## Recovery

Restore a previous successful Netlify deploy, or revert a publication commit. Do not force push or delete the public history as a routine rollback.
