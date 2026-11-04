# GhostMesh Scout | Owner-authorized private commissioning receipt

Date: 2026-10-23. Owner explicitly approved encrypted off-host backup and daily private Scout collection.

## Operational status

**ACTIVE:** one owner-private GhostMesh VPS cron entry evaluates hourly at minute 00 and only executes collection at local 08:00 in `America/Los_Angeles`. This UTC-independent local-hour check accommodates Pacific daylight saving transitions. The first run after installation is scheduled for **2026-10-24 at 08:00 PDT**. No successful scheduled run can be claimed until this future occurrence is witnessed.

Cron entry (marker `ghostmesh-scout-daily-v1`):

```cron
0 * * * * /usr/bin/flock -n /home/ghostmesh/.local/share/ghostmesh-scout-pilot/.scout-daily.lock /home/ghostmesh/.local/share/ghostmesh-scout-app/scripts/scout_scheduled_collection.sh --daily >> /home/ghostmesh/.local/share/ghostmesh-scout-pilot/.scout-daily.log 2>&1 # ghostmesh-scout-daily-v1
```

One entry verified; the active cron service and existing unrelated entries were preserved. An out-of-window `--daily` test correctly printed `Not 08 Pacific; exit`.

- Pinned source checkout: `/home/ghostmesh/.local/share/ghostmesh-scout-app` at `60b1d8685a697172293dae593f4fe10bf68f0a96`, draft PR #65
- Manual/cron runner: `scripts/scout_scheduled_collection.sh`, caps collection at 3 public records per source, calls the integrity-protecting `scout_manual_operator.py`
- Private run root: `/home/ghostmesh/.local/share/ghostmesh-scout-pilot`
- Operator-facing private run library generated separately from research receipts
- Cron lock and log in private root: `.scout-daily.lock`, `.scout-daily.log`
- **No automatic deletion, public hosting, source publication, contributor outreach, or external model inference**

## Off-host encrypted backup qualification

Hyperion-96 SSH server's ED25519 fingerprint was independently read from the connected Hyperion machine:
`SHA256:TD84LORwj/PRzcZbhYm+UWk5X0iLkpnxIElJCsKK/Q0`.

VPS private `scout_backup_known_hosts` pins that verified public key under the dedicated alias `hyperion-scout-backup`. SSH always uses `StrictHostKeyChecking=yes` and `BatchMode=yes`, with a dedicated backup key, rather than accepting host keys automatically.

On Hyperion, that key is limited through OpenSSH `restrict,command=` to `scout_backup_receiver.py`, which permits only bounded encrypted archive upload, digest readback, and retrieval under:
`/home/tony-malott/.local/share/ghostmesh-scout-encrypted`.

Archive encryption uses a newly generated OpenPGP key under Hyperion owner's private GPG home:
`/home/tony-malott/.gnupg-scout-backup`.
Recipient primary-key fingerprint:
`9E697D0D47B4BC77A5678C084AF4665FF7551612`.
Only its public encryption key was imported into the VPS owner-private GPG home. The decryption secret key stays on Hyperion. Protect and back up that private key and its storage separately, because host loss would otherwise prevent decrypting saved archives.

Manual off-host witnesses:
1. `pilot-20261023-manual-operator-01.tar.gpg` transferred to Hyperion. Source and destination encrypted archive digest matched: `62a12ebed41c256b05e83e3523d7267e735eeb43a6f1e4685f62cd9e7217bef6`.
2. Hyperion successfully decrypted and restored its **14 research files** to a separate restricted test directory, with **zero manifest hash mismatches** and ten workspace panels.
3. The installed scheduler backup script also transferred `pilot-20261023-browser-qa-final.tar.gpg`, with source/remote encrypted digest match `e70cd5e41d2610e43181c82c0d4fab1b522312e535b2610743b3565a1bb324c1`.

No backup archive overwrite or automatic pruning is permitted. Failures leave local run evidence preserved and print an error in the private cron log.

## Monitoring and immediate rollback

Check recent runs and errors using:
```bash
python3 /home/ghostmesh/.local/share/ghostmesh-scout-app/scripts/scout_private_archive.py inventory --root /home/ghostmesh/.local/share/ghostmesh-scout-pilot
tail -n 80 /home/ghostmesh/.local/share/ghostmesh-scout-pilot/.scout-daily.log
crontab -l | grep ghostmesh-scout-daily-v1
```

**Disable the schedule without deleting research**: edit only the `ghostmesh-scout-daily-v1` line from the `ghostmesh` user's `crontab -e`, leaving all other GhostMesh entries intact. The private archive and run files are preserved. Re-enable only the same reviewed cron entry after repairing any failure.

## Remaining limitations

- The current private collector is metadata-first. Claim validity, authorship identity, originality, GhostMesh capability improvement and contributor contact remain unverified; those labels are not uplifted by scheduling.
- No notification is currently dispatched on a failed scheduled run; examine the local private log. Separately approved failure alerting can be added later if needed.
- GPG recipient secret key was generated on Hyperion without a passphrase to allow unattended decryption there; its safety therefore depends on Hyperion account, filesystem and host security. Independent recovery escrow for this decryption key is not yet qualified.
- The first genuinely scheduled run after activation has not yet occurred. Do not claim a 24-hour production reliability window or continuous social-media coverage.
- Private host access only. No public source snapshots, credentials or transcripts are published.
