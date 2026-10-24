# GhostMesh Scout | Controlled activation decision

Status: **OWNER APPROVAL REQUIRED**. Prepared 2026-10-23 for draft PR #65. This is an operational decision record, not permission to deploy.

## Current reality

- Ten-panel owner-private Scout research workspace is operational via manual invocation on the unprivileged GhostMesh VPS account.
- Three recorded owner-private runs pass checksum verification; most recent run reports 12 public streams and zero source errors.
- Owner-private research root: `/home/ghostmesh/.local/share/ghostmesh-scout-pilot` (0700, outputs 0600).
- A same-VPS backup and restore-copy exercise has passed; **no off-host disaster recovery is commissioned**.
- Interactive Chrome tab-click and keyboard navigation passed; 390px emulated viewport showed no outer page overflow. Real-device accessibility and ten-panel source-content review are not fully qualified.
- The research PR is draft and must not be interpreted as a live private-hosted service.
- There is no automatic scheduling, public release, outbound contributor contact, or credential authority.

## Recommended initial operational policy (proposal, NOT activated)

1. **Daily private collection at 08:00 America/Los_Angeles.** Use the current `scout_manual_operator.py` entrypoint with capped public inputs. On collection failure, report the failure and preserve the last verified run. Do not repeat endlessly.
2. **Off-host encrypted archive to Hyperion-96**, restricted to an explicitly approved owner-private directory, without granting GhostMesh broad filesystem access or introducing shared secrets into the repository. Each copied archive must be integrity-verified after transfer. No off-host transfer until operator identity and destination are approved.
3. **Keep all runs initially.** Recommend 30-day *review*, not 30-day automatic deletion: a later archival/pruning change needs an explicit owner retention decision. No silent deletion.
4. **Private-only access** through already authorized owner pathways. No public URL, guest access, unsolicited outreach, external model-provider uploads, or publishing of full source snapshots.
5. **Release gate:** one manually triggered off-host backup and restore witness, verification of permissions, and confirmation that scheduled delivery does not collide with other owner jobs. Operator may disable the timer immediately; archive is never deleted by rollback.

## Off-host readiness witness

- VPS resolves the Tailscale hostname `hyperion-96` to an internal tailnet address.
- Hyperion's intended `tony-malott` account is an existing owner account; its local private storage is available.
- A read-only strict-host-key SSH probe `ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=yes tony-malott@hyperion-96 true` was **refused**: no known ED25519 host key, so host key verification failed.
- This is a **security guardrail working correctly**, not authorization to disable checking. Before any transport, independently verify Hyperion's public SSH host fingerprint through an already trusted owner pathway, then explicitly approve the destination and access method. Never accept an unverified `ssh-keyscan` response as identity proof.

## Risks and rollback

- Collection sources can throttle or vanish: previous verified run remains readable; no assumptions of continuous monitoring or representative social coverage.
- Source metadata can be adversarial: keep contents as data, with source links, timestamps and confidence boundaries, never as instructions or verified claims.
- A leaked private archive could expose reading interests and research plans: encrypt before transfer, validate recipients and destination, restrict permissions, keep private keys out of repo and logs.
- Disable a future schedule without touching research receipts. Preserve original runs, turn off hosted exposure if separately enabled, and use the previously witnessed manual operator command.

## Owner decisions requested

**A.** Authorize private off-VPS backup commissioning to Hyperion under a verified SSH host identity and designated private destination, with encryption and a first manual restore test?

**B.** Authorize a daily 08:00 Pacific private Scout collection schedule *after* the off-host backup witness, retaining runs without automatic deletion pending separate retention approval?

These are separate authorization boundaries. A conversational “next” has not been interpreted as approval to transfer private research or enable a timer.

## Implementation references

- `scripts/scout_manual_operator.py`
- `scripts/scout_private_archive.py`
- `scripts/scout_run_library.py`
- `research/SCOUT-METHODOLOGY.md`

Do not add another experimental research requirement to prevent this low-risk owner-private Scout from becoming useful. Remaining source-body analysis is an explicit future capability, not an excuse to withhold manual collection.
