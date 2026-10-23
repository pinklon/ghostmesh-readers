# Scout commissioning readiness: first-run and replay pilot

Date: 2026-10-23. Owner-private read-only research, draft PR #65.

## Change

The integrated Scout runner now builds all nine private workspace views without requiring any historical HTML view manifest. It rejects legacy view inputs rather than silently mixing obsolete panels with fresh evidence. A first collection has an explicit **AWAITING_PRIOR_SNAPSHOT** History panel, and a subsequent collection supplied with the first intake regenerates a two-snapshot history.

The single-command interface remains:
`python3 scripts/scout_integrated_run.py --run-root <private pilot folder> --run-id <unique name> --catalog research/scout-watch-catalog-v0.json --cap 3`

A second run may add `--previous <previous-run>/intake.json`. Neither command schedules itself.

## Observed qualification

Isolated GhostMesh VPS, unprivileged temporary directory `/tmp/scout-trial-34Lfv9/commission-pilot`, no production writes:

| One-shot run | Public streams | Errors | Leads | Reading candidates | Panels | History |
|---|---:|---:|---:|---:|---:|---|
| collection-a | 12 | 0 | 36 | 13 | 9 | AWAITING_PRIOR_SNAPSHOT |
| collection-b | 12 | 0 | 36 | 13 | 9 | TWO_SNAPSHOT_REBUILT |

All artifact SHA-256 digests in both run manifests matched, with no omissions. Source counts in this small top-three sample are not claims of ecosystem coverage, popularity trends or verified intelligence.

After removal of the legacy setup path, **290 Scout tests PASS** on the isolated VPS at commit `6cb4568a`. This qualification does not prove the local workspace has been browser-rendered or that the system is a running service.

## Next commissioning requirements

1. Browser-level visual and interaction review, including mobile width, navigation, direct source links and methodology.
2. Agree on a **durable owner-private run root** with minimal filesystem permissions and a manual operator invocation. Temporary `/tmp` output is disposable and not acceptable as a production data store.
3. Confirm retention, failed-run cleanup, and atomic receipt recovery without irreversible source deletion.
4. Explicit owner approval separately for a production path, hosted private access and recurring collection. Do not default to scheduled deployment.

The nine panels describe metadata observations, topic heuristics and proposed questions with deliberate uncertainty. Scout is not yet a verified source-content analyst or autonomous collaborator scout. No account connections, credentials, external outreach, production scheduling or public publishing.
