# Scout full-workspace commissioning pilot receipt

Date: 2026-10-23. Research-only, no production scheduler, deployment or permissions change.

## Integration implemented

`scripts/scout_integrated_run.py` now accepts `--views-manifest`: an explicit JSON mapping of the eight existing, previously generated HTML research views. It generates the current Discovery view from collection/triage/reconciliation, uses the existing `scout_workspace.build()` to assemble the nine-view shell, inserts a run-level methodology link, and **visibly labels all other panels pinned historical snapshots**. The research run manifest discloses `workspace_view_status`; nothing claims that the old views were recomputed against new signals.

One-shot run command (isolated VPS, redacted root paths here):

`python3 scripts/scout_integrated_run.py --run-root <private-root> --run-id full-workspace-20261023-01 --catalog research/scout-watch-catalog-v0.json --offline-intake <captured-current-snapshot> --previous <prior-snapshot> --views-manifest <eight-view-path-manifest>`

The manifest is an explicit input. This is **not** a continuous service, not an autonomous model researcher, and not yet a fully live-updating nine-panel Scout. Subsequent work must migrate history, claims, people, trails and theses from pinned artifacts into per-run pipelines based on the captured evidence.

## Qualification witnessed

- **288 Scout tests PASS** from the current PR branch on isolated GhostMesh VPS.
- Full workspace run: **95 observed public signals**, **33 reading candidates**, **9 panels**.
- Artifact manifest: **eight SHA-256-verified outputs**, plus `manifest.json`; zero digest mismatches.
- Private methodology linked from the workspace shell, supplied by `research/SCOUT-METHODOLOGY.md`.
- Artifact directory on isolated VPS: `/tmp/scout-trial-34Lfv9/integrated-runs/full-workspace-20261023-01`.
- Copied to Tony's Mac Studio: `~/Downloads/GhostMesh-Scout-Private-Review/scout-integrated-nine-view-pilot/workspace.html`, with nine files copied and zero hash mismatches.

## Guardrails and real next steps

The prior research snapshots may have been generated at different collection times, so they are reference evidence, not fresh results. Before commissioning a repeatable Scout service: (1) regenerate the key analysis views from each immutable intake run, (2) establish read-only operator invocation/persistence in the intended private operational directory, (3) qualify freshness, source failure and rollback, (4) separately authorize any schedule or hosted release.

No model inference, third-party accounts, outreach, credentials, public article publication, database mutation, or production infrastructure change.
