# Scout commissioning: private archive and retention pilot

Date: 2026-10-23. Draft PR #65. No production scheduler.

## Verified

New `scripts/scout_private_archive.py` implements a **one-shot, non-destructive** copy of an owner-private Scout run and verifies SHA-256 on every saved artifact before and after copying. It rejects permissive or symlinked run roots, unexpected files, missing receipts, and mutated content. Backup destinations must be private and may not already exist.

A second command inventories private run folders and reports integrity without pruning or deleting anything.

On the isolated VPS:
- **299 Scout tests PASS**.
- Original pilot: `/home/ghostmesh/.local/share/ghostmesh-scout-pilot/pilot-20261023-browser-qa-final`.
- Verified archive copy: `/home/ghostmesh/.local/share/ghostmesh-scout-pilot-backups/pilot-20261023-browser-qa-final`.
- **14 files verified**, including manifest. Original preserved, no automatic deletion.
- Inventory scanned the two existing research pilot runs. Both were **VERIFIED**, zero deleted, retention `KEEP_UNTIL_OWNER_POLICY`.

## Boundaries

This is a filesystem-level recovery copy on the **same VPS**. It does not protect against VPS disk loss, compromised user credentials, or provider failure, and is **not** an off-host backup. No retention expiration or automatic deletion policy has been authorized. Before production scheduling, the owner should approve an off-host private backup destination and recovery/retention terms.

Browser QA from the previous increment confirmed the desktop interface rendered in headless Mac Chrome with a bounded wait. It did not qualify real interactive keyboard navigation, tab selection or mobile use. Those remain usability tasks, not reasons to add more governance machinery.

No production deployment, external publication, contact, login, new credentials, or automatic recurring collection.
