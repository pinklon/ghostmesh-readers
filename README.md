# GhostMesh Readers

The public, video-first companion to [SharePlane](https://shareplane.malott.ai/). The Readers site is deliberately separate from SharePlane Production and private ReasonPack processing.

**Live collection:** https://youtube.shareplane.malott.ai/

**Netlify project:** `shareplane-youtube` (existing site ID: `27352ed6-0f74-4756-832e-95ba49e31b09`). **Publish directory:** `site/`, configured by `netlify.toml`; no dependency installation or build command.

## Add a Reader

1. Create `site/<slug>/index.html`. Embed the original YouTube video prominently, with a direct YouTube fallback and chapter links.
2. Preserve a separate GhostMesh editorial thesis, inspectable evidence sources, and honest qualifications.
3. Update the collection in `site/index.html` and `site/sitemap.xml`; keep all existing slugs.
4. Run `python3 scripts/check_site.py` before publication. GitHub Actions verifies pull requests and pushes.
5. Review the proposed change and merge into `main`. Netlify will deploy automatically **after** this existing project is connected to the repository.

## Hosting separation

The public site is immutable, static Git content. Mac Studio, Hyperion and the GhostMesh VPS can propose new content but none is required to keep the site available. Each production deployment must be traceable to a Git commit. Do not publish private media packs, email addresses, credentials, machine paths, private agent histories, or nonpublic SharePlane Works.

## One-time connection

In the **existing** Netlify project `shareplane-youtube`, connect GitHub repository `pinklon/ghostmesh-readers`, production branch `main`. Do not create another Netlify project or modify Cloudflare DNS. Confirm the build settings show `site/` as publish directory and no build command. The live domain must remain `youtube.shareplane.malott.ai`. Connection is an account-owner step and is **not** implied by these Git files.

## Recovery

Restore a previous successful Netlify deploy, or revert a publication commit. Do not force push or delete the public history as a routine rollback.
