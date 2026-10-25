#!/usr/bin/env bash
# GhostMesh Scout owner-private one-shot collection and encrypted off-host backup.
set -euo pipefail
umask 077
APP=/home/ghostmesh/.local/share/ghostmesh-scout-app
ROOT=/home/ghostmesh/.local/share/ghostmesh-scout-pilot
LOCAL=/home/ghostmesh/.local/share/ghostmesh-scout-pilot-backups
GPGHOME=/home/ghostmesh/.gnupg-scout-send
SSHKEY=/home/ghostmesh/.ssh/scout_backup_ed25519
KNOWN=/home/ghostmesh/.ssh/scout_backup_known_hosts
RECIPIENT=9E697D0D47B4BC77A5678C084AF4665FF7551612
mkdir -p "$LOCAL"
chmod 700 "$LOCAL"
backup_run() {
    local run="$1" name archive local_hash remote_hash
    name=$(basename "$run")
    archive="$LOCAL/$name.tar.gpg"
    test ! -e "$archive" || { echo "Archive exists, refusing overwrite: $name" >&2; return 1; }
    python3 "$APP/scripts/scout_private_archive.py" inventory --root "$ROOT" >/dev/null
    tar -C "$run" -cf - . | gpg --batch --yes --trust-model always --homedir "$GPGHOME" -r "$RECIPIENT" --encrypt -o "$archive"
    chmod 600 "$archive"
    local_hash=$(sha256sum "$archive" | awk '{print $1}')
    ssh -i "$SSHKEY" -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$KNOWN" -o HostKeyAlias=hyperion-scout-backup -o ConnectTimeout=10 tony-malott@hyperion-96 "scout-put $name.tar.gpg" < "$archive"
    remote_hash=$(ssh -i "$SSHKEY" -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$KNOWN" -o HostKeyAlias=hyperion-scout-backup -o ConnectTimeout=10 tony-malott@hyperion-96 "scout-digest $name.tar.gpg" | awk '{print $1}')
    test "$local_hash" = "$remote_hash" || { echo "REMOTE HASH MISMATCH: $name" >&2; return 1; }
    echo "VERIFIED_OFF_HOST_BACKUP $name $remote_hash"
}
case "${1:-}" in
  --backup-existing)
    test "$#" -eq 2
    backup_run "$ROOT/$2"
    ;;
  --daily)
    test "$#" -eq 1
    if test "$(TZ=America/Los_Angeles date +%H)" != "08"; then echo "Not 08 Pacific; exit"; exit 0; fi
    run_id="$(date -u +scout-%Y%m%dT%H%M%SZ)"
    python3 "$APP/scripts/scout_manual_operator.py" --root "$ROOT" --run-id "$run_id" --catalog "$APP/research/scout-watch-catalog-v0.json" --cap 3
    backup_run "$ROOT/$run_id"
    ;;
  *) echo "usage: $0 --daily | --backup-existing <run_id>" >&2; exit 2;;
esac
