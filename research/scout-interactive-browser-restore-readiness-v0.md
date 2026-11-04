# Scout commissioning: interactive Chrome QA and non-destructive restore exercise

Date: 2026-10-23. Research-only staging, draft PR #65. No production scheduling.

## Browser interaction results

The owner-private Scout workspace `scout-commission-pilot-final/workspace.html` was exercised using local headless Google Chrome on Tony's Mac Studio. Chrome DevTools Protocol commands executed actual UI events. Results:

- Ten tabs and ten panels present
- Exactly one visible panel on initial load
- Clicking the Relationships tab showed `panel-relationships`
- Focusing Relationships and pressing ArrowRight selected History
- Navigation uses `flex-wrap: nowrap` with horizontal scrolling when needed
- At a 390px emulated mobile viewport, `document.documentElement.scrollWidth = 390` and viewport width = 390, so no observed outer-page horizontal overflow
- Mobile tab strip remained scrollable, with scroll width 1436px inside its own 390px viewport
- The test is headless Chrome emulation, **not** manual real-phone touch, VoiceOver/screen-reader testing, or all-panel content acceptance.

The prior screenshots displayed a timing-related initial blank iframe until the browser was given a virtual-time budget. Subsequent renders displayed Discovery. This did not recur as a functional error during the Chrome interaction check.

## Recovery exercise

The private Scout pilot snapshot was copied and hash-verified from the existing same-VPS backup into a **separate** owner-private restore-test directory:
`/home/ghostmesh/.local/share/ghostmesh-scout-pilot-restore-test/pilot-20261023-browser-qa-final`

Results: 14 files verified; original preserved; no automatic deletion or source overwrite. This is a restore-copy exercise on the same VPS, **not** a test of disaster recovery after loss of the VPS.

## Off-host destination review only

Hyperion-96 is connected under the owner's `tony-malott` user, with approximately 893 GB free in the inspected home filesystem. Its `~/.local` and `~/.local/share` directories are private (0700). GPG is available. **No Scout research content, encryption keys, credentials or backups were transferred to Hyperion**, and no access permissions were changed. An off-host backup destination and transport/encryption policy still need owner approval.

## Remaining commissioning boundaries

Interactive desktop navigation and emulated 390px width are witnessed; full mobile/touch/accessibility review remains. Owner-private durable staging, checksum-verified same-host copy and restore exercise are qualified. Off-host disaster recovery, retention duration, recurring schedule, and production exposure are **not** commissioned.

No public deployment, cron/systemd timer, privileged permissions change, or author outreach.
