# Scout private run library | Operator checkpoint

Date: 2026-10-23. Draft PR #65, owner-private pilot only.

Added `scripts/scout_run_library.py` to generate one **read-only landing page** across the run directories already verified by Scout's private archive checker. It shows capture timestamps, observed leads, reading candidates, source fetch/error counts, and the source-history status, linking directly to each run's `workspace.html`.

It never alters or prunes a research run, needs no network/credentials, refuses output inside the immutable run root, and does not present unverified or corrupted runs as valid. The page is a separately generated private HTML file (mode 0600) outside the run root. Links are relative to its private VPS location.

## Witnesses

- 306 Scout tests passed on the isolated VPS.
- Ran against `/home/ghostmesh/.local/share/ghostmesh-scout-pilot`: **three verified runs**, newest `pilot-20261023-manual-operator-01`, newest capture with zero source errors.
- Generated `/home/ghostmesh/.local/share/scout-private-runs-20261023.html`, mode 0600.
- All three links resolve to existing private Scout workspace files, none leave the intended Scout research root.
- No run files were overwritten, deleted, or made public.

## Operator command

`python3 scripts/scout_run_library.py --root /home/ghostmesh/.local/share/ghostmesh-scout-pilot --out /home/ghostmesh/.local/share/scout-private-runs-<unique-date>.html`

Use a new output name per execution; existing indexes are never overwritten.

## Remaining production boundary

This landing page is not a hosted private application. The index and its links operate within the connected owner's private VPS filesystem. No off-host backup, scheduler, authentication bridge, public deployment, external outreach or production integration was authorized.
