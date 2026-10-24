# Scout manual operator quickstart

Owner-private research pilot, 2026-10-23. No scheduled or hosted deployment is authorized.

## Running Scout once

The only required inputs are a unique run ID and the existing owner-private research root. The operator verifies existing runs and automatically selects the most recently captured valid intake as its chronological baseline.

```bash
python3 scripts/scout_manual_operator.py \
  --root /home/ghostmesh/.local/share/ghostmesh-scout-pilot \
  --run-id "$(date -u +scout-%Y%m%dT%H%M%SZ)" \
  --catalog research/scout-watch-catalog-v0.json \
  --cap 3
```

This is an **explicit manual command**, not a timer, cron, systemd unit, autonomous outreach process, or model agent. It makes public-source GET requests only and returns paths and counters. For offline reproduction, use `--offline-intake /path/to/intake.json`; the input must represent a later capture than the selected prior run.

Each run writes `workspace.html`, `methodology.html`, the original `intake.json`, analysis JSON files, and a SHA-256 manifest into a **new private directory**. The runner refuses duplicate run IDs, shared directories, invalid receipts, and a capture timestamp older than its last verified baseline. Existing run files are never overwritten.

## Verification and preservation

```bash
python3 scripts/scout_private_archive.py inventory \
  --root /home/ghostmesh/.local/share/ghostmesh-scout-pilot
```

The inventory is read-only and never deletes research. To create a verified same-VPS recovery copy, explicitly run `scout_private_archive.py backup --run <run-folder> --dest <new-private-destination>`. No automatic pruning policy is implemented.

**Safety and epistemic limits:** A successful collection means data was retrieved and categorized, not that source claims were verified, named people identified, or GhostMesh capability gains measured. Public and owner-private results remain separate. The workspace's ten panels record distinct evidence grades, including a Source Reviews placeholder until primary-source inspection actually occurs.

## Pilot witness

On 2026-10-23 the isolated VPS ran `pilot-20261023-manual-operator-01`: 12 public streams, 36 leads, 13 reading candidates, zero source errors, prior verified run selected automatically, and two-snapshot history rebuilt. All generated file hashes matched; the research directory mode is 0700, and output files are 0600. The current branch passed **303 Scout tests**.

## Not commissioned

- An off-VPS encrypted backup destination and transfer procedure
- A production retention/restore policy across host loss
- Recurring execution cadence, service scheduling, or hosted private access
- Any external contributor outreach, privileged infrastructure changes, or public research publication

Hyperion-96 has been inspected as a possible owner-controlled off-host destination. No data, keys or credentials have been moved to it. **Explicit owner authorization is required for the transfer and recurring schedule.**

No additional governance automation is a prerequisite to continuing manual pilot use.
