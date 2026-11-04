# Scout commissioning readiness: private storage and Chrome browser QA

Date: 2026-10-23. Scope: reversible research-only pilot in draft PR #65.

## Operational staging, not production deployment

Using the unprivileged GhostMesh service account (UID 1001), a new private pilot root was established at:

`/home/ghostmesh/.local/share/ghostmesh-scout-pilot`

Witnessed mode and integrity:
- Run root **0700** and generated run directory **0700**
- Generated research artifacts **0600**, owned by the service account
- No symlinked run root accepted and permissive run directories rejected
- First pilot `pilot-20261023-commission-a` collected **36 public signals**, **12 reading candidates**, and all **12/12 retrieval streams** without reported source errors
- Second pilot `pilot-20261023-browser-qa-final` replayed that snapshot, supplied an earlier snapshot, and rebuilt source history
- First pilot: **12 generated artifact hashes verified**, ten panel HTML sections, no earlier history falsely claimed
- Second pilot: 13 generated artifacts plus manifest, two-snapshot history
- No account credentials, operator secrets, production scheduler, or public host access configured

The staging directory is durable relative to `/tmp`, but there is **no qualified backup, retention policy, recovery after machine loss, or service-level persistence guarantee** yet. It is not a production datastore.

## Browser checks and fixes

Mac Studio Chrome headless rendered the owner-private Scout workspace at a desktop viewport of 1366×900. The initial screenshot briefly showed blank embedded content, but a second run with a 3-second virtual-time budget displayed Discovery correctly. Treat this as screenshot timing evidence, not proof of a broken browser navigation path. A narrow-window screenshot was also captured. It showed some clipping on the right edge; headless Chrome may enforce a minimum window width, so the exact cause remains unverified. **Interactive mobile usability is still not qualified.**

Concrete reversible improvements committed:
- `scout_workspace.py`: keep all ten tabs in one horizontally scrollable row instead of wrapping into an awkward second row
- `scout_multi_source_preview.py`: avoid unbroken source timestamps and header links forcing mobile overflow
- `scout_integrated_run.py`: require private run roots and owner-only artifact files
- `tests/test_scout_integrated_run.py`: private permissions and rejecting shared roots

The current PR branch passed **295 isolated-VPS Scout tests** at commit `9caf2174`.

## Mac review copy

A self-contained **five-file viewing bundle** was copied to:

`~/Downloads/GhostMesh-Scout-Private-Review/scout-commission-pilot-final/`

It contains `workspace.html`, `index.html`, `methodology.html`, `methodology.md` and `manifest.json`. All copied generated files verified against the manifest digests. The complete underlying JSON dataset remains in the private VPS run directory and was **not** transferred in this lightweight Mac preview.

## Commissioning blockers that remain real

- Interactive keyboard, mobile-width and full-ten-panel browser acceptance, not just initial render
- Durable backups/retention and source-error recovery procedure
- Owner signoff for final private production location and any recurring schedule
- Privacy exposure review if a hosted interface is enabled

No production install, scheduled collection, publication, outreach, paid inference, or authentication change occurred.
