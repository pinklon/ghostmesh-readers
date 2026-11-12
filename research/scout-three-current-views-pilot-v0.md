# Scout integrated graph and timeline qualification | 2026-10-23

Research-only pilot for draft PR #65.

The integrated Scout command now regenerates **three** views from the actual captured run rather than copying all eight older panels:
- **Discovery**: current intake/triage/reading queue.
- **Relationships**: current-run graph, with 95 public source nodes, 22 metadata-topic links and 25 observed-handle links. These links are metadata relationships, **not social relationships or verified identities**.
- **History & revisions**: a two-snapshot observation history, with 106 distinct URLs across the sampled windows, 48 repeated sightings and 11 absent from the latest sample. The 11 absences do **not** prove deleted sources. The 11 recorded metadata events may include sampling-only absence events; they are not all substantive source revisions.

The other **six views are pinned historical research**, visibly disclosed in the nine-tab workspace. No fresh claim, person, thesis, or capability audit is implied.

## Implementation and evidence

- `scripts/scout_integrated_run.py` calls the existing `scout_relations.build()`, `scout_relationship_preview.render()`, `scout_source_history.build()`, and `scout_history_preview.render()`. It stores `relations.json` and `history.json` alongside the existing outputs.
- It only regenerates History when a previous snapshot exists with an earlier timestamp; without a qualifying earlier snapshot, the supplied historical History view is retained with a pinned label.
- Current branch's **288 Scout tests passed** on the isolated GhostMesh VPS before the pilot.
- Pilot run: `/tmp/scout-trial-34Lfv9/integrated-runs/three-live-views-20261023-01/`.
- **10 generated research artifacts** plus manifest; every listed SHA-256 matched (zero mismatches).
- Nine panel HTML workspace present.
- Copied to Tony's Mac Studio: `~/Downloads/GhostMesh-Scout-Private-Review/scout-integrated-three-current-views/workspace.html`, 11 files including the manifest, with zero verification failures.
- Full methodology remains linked and bundled.

No production service, scheduler, model inference, permissions, publication, or outreach. Next integration candidates are claims and public-source work trails, but only from real source evidence and without inventing people or relationships.
