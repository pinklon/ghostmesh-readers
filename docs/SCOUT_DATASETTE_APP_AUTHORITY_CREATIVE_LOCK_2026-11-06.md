# Scout Datasette app authority: Creative Lock review packet

Status: **PENDING final public-copy lock and release date**. This is an implementation specification, not Production authorization.

## Authority, lane and identity

- Owner and UAT: Tony Malott. Editorial co-development: Tony and segfault. Mechanical implementation only after lock.
- Repository: `pinklon/ghostmesh-readers`; draft PR #123, branch `segfault/scout-datasette-app-authority-draft-20261106`.
- Lane: GhostMesh Scout original research essay, not a standing routine source report.
- Title: **The Agent Can Build the App. Who Lets It Touch the Data?**
- Slug: `the-agent-can-build-the-app-who-lets-it-touch-the-data`.
- Canonical target: `/scout/essays/the-agent-can-build-the-app-who-lets-it-touch-the-data/`.
- Source: `content/scout/publication-drafts/23-the-agent-can-build-the-app-who-lets-it-touch-the-data.md`, staged in commit `f2c4e63dd149e7ab30ff270d0217b45d056b3635`.
- Original local SHA-256 before GitHub staging: `84c83a815c90071321792f9b50c1d9eacf3211b8f04b3b699bd4e052ac9bb8de`.
- Audience: agent builders, security architects, data platform owners, and operators of consequential workflows.

## Meaning, evidence and disclosure

- Thesis: Generating an application does not grant it authority over the data operations behind it. Separate app authorship, specific grants, viewer-level execution rights, and auditable revisions.
- Public-copy posture: preserve all substantive paragraphs, sequence, source links, caveats, objection, independent-test proposal, and relationship rationales from the staged manuscript without compression.
- Editorial metadata lines beginning `Scout editorial draft` and `Publication projection requirement:` are workflow instructions, not article prose. The exact cleaned public copy must be accepted before rendering.
- Primary sources: Datasette Apps 0.3a0 release November 4, 2026, upstream PR #43, and Simon Willison's November 4 release note.
- Source role: the upstream release and PR are primary product/implementation evidence; Simon's note is primary release context, not independent corroboration; the two earlier Scout essays are internal conceptual relationships, not evidence about Datasette.
- Claim limit: source-based editorial analysis only. No GhostMesh installation, execution test, penetration test, independent regression reproduction, or certification. Laboratory example is hypothetical.
- Public safety: no employer, client, internal GhostMesh credential, private Scout packet, or personal information is to be introduced. No imagery or proprietary materials.
- Required disclaimer: `Source-based editorial analysis only. No local installation, runtime experiment, penetration test, or independent validation of the upstream passing checks. Hypothetical laboratory examples illustrate design consequences, not observed incidents.`

## Design and target files

- Reuse `/scout/essays/the-approval-must-survive-the-summary/` as the strongest comparable Scout essay wrapper: site header/nav, stylesheet, hero, editorial typography, responsive behavior, accessible article, theme behavior, and footer.
- No new imagery, visual prompts, runtime dependencies, analytics, background tasks, or JavaScript behavior.
- Candidate HTML: `site/scout/essays/the-agent-can-build-the-app-who-lets-it-touch-the-data/index.html`.
- Canonical research register: `content/scout-research.json`, one add-only `essay:` record. Topical tags: `agent-authority`, `data-permissions` (final acceptance pending).
- First-publication event: `content/public-release-events.json`, only once actual intended public date is accepted. Never use the draft date as proof of publication.
- Deterministic outputs: generated Scout Library, landing, relationship JSON, sitemap and feed from existing `scripts/generate_site.py`. Existing curated essay index must include a matching card if the comparable precedent requires it.
- Focused acceptance checks: current `tests/test_scout_research.py`, `tests/test_scout_feed.py` and static site checks; add focused tests only for a genuine coverage gap.
- Receipt: PR #123 body plus a scoped validation report, with exact candidate SHA, commands, CI, preview and live-post-merge outcomes.

## Relationships: proposed and editorially accepted in principle

Disposition: `RELATIONSHIPS_ACCEPTED` for two named links in the manuscript, contingent on exact public-copy lock and preview confirmation.

1. **Policy parallel**: `essay:assisted-permissions-and-human-approval`, `/scout/essays/assisted-permissions-and-human-approval/`. Prior analysis tests what a human-approval rule means when an AI helper can judge whether to ask.
2. **Architectural extension**: `essay:the-approval-must-survive-the-summary`, `/scout/essays/the-approval-must-survive-the-summary/`. Prior analysis addresses survival of a pending authorization and its execution owner across handoff and summarization.

Both must appear under `Follow the thinking` with distinct rationale; `relatedIds` must contain the exact two canonical IDs. Confirm projected `scout:` graph edges and both destinations. Neither relationship is independent corroboration of Datasette's implementation. No `dependsOn`, `supports`, or pattern dependency is asserted beyond the existing Scout graph schema.

## Required checks and release boundary

- Run `python3 scripts/generate_site.py`, `python3 scripts/generate_site.py --check`, `python3 scripts/check_site.py`, and `python3 -m unittest discover -s tests -p 'test_*.py'` plus `git diff --check`.
- Confirm canonical, Library card, curated index card, relationship JSON edges, sitemap, feed uniqueness, no private imports, and no `noindex` on a release candidate.
- Review Netlify preview on desktop and narrow mobile widths: navigation, links, reading measure, overflow, theme and console health.
- All registry/publication/event changes remain on draft PR #123 until explicit unchanged-head owner authorization. Auto-merge prohibited. Rollback before merge is PR close; after merge, revert via existing repository and Netlify path with a correction if feed subscribers received an event.

## Open lock decisions

- The committed source begins `Not approved for publication`. Tony's conditional endorsement of the argument and relationships is recorded, but the final exact cleaned public-copy hash has not been accepted.
- The actual first-publication date and its event are uncommitted. Production timing cannot be inferred from drafting time.
- Final metadata tags and the exact cleaned copy need an affirmative Creative Lock decision; until then no registry mutation or public release is authorized.

Gate: **HOLD at Creative Lock**. Codex prompt needed: none until the open choices are resolved.
