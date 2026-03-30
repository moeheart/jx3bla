#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  tools/migrate_old_stat_files.sh --remote user@host --remote-dir /path/to/jx3bla \
    --local-dir /path/to/backup --cutoff 2025-01-01 [--mode tar|rsync] [--compress none|gzip] [--delete-remote] [--dry-run]

What it does:
  - Selects files under:
      database/ActorStat/
      database/ReplayProStat/
    whose mtime is earlier than the cutoff date.
  - Transfers them to local backup directory.
  - By default does NOT delete remote files.
  - Use --delete-remote to delete the source files on the remote after a successful transfer.

Notes:
  - Default mode is "tar" (streaming, minimal remote disk usage).
  - Use "--compress gzip" to reduce transfer size (recommended on low bandwidth).
  - "rsync" mode requires rsync on BOTH local and remote; it deletes per-file after transfer.

Examples:
  tools/migrate_old_stat_files.sh --remote root@1.2.3.4 --remote-dir /srv/jx3bla \
    --local-dir ./backup --cutoff 2025-01-01

  tools/migrate_old_stat_files.sh --remote root@1.2.3.4 --remote-dir /srv/jx3bla \
    --local-dir ./backup --cutoff 2025-01-01 --mode rsync
EOF
}

REMOTE=""
REMOTE_DIR=""
LOCAL_DIR=""
CUTOFF=""
MODE="tar"
COMPRESS="none"
DRY_RUN=0
DELETE_REMOTE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      REMOTE="$2"; shift 2;;
    --remote-dir)
      REMOTE_DIR="$2"; shift 2;;
    --local-dir)
      LOCAL_DIR="$2"; shift 2;;
    --cutoff)
      CUTOFF="$2"; shift 2;;
    --mode)
      MODE="$2"; shift 2;;
    --compress)
      COMPRESS="$2"; shift 2;;
    --delete-remote)
      DELETE_REMOTE=1; shift 1;;
    --dry-run)
      DRY_RUN=1; shift 1;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2;;
  esac
done

if [[ -z "$REMOTE" || -z "$REMOTE_DIR" || -z "$LOCAL_DIR" || -z "$CUTOFF" ]]; then
  usage
  exit 2
fi

mkdir -p "$LOCAL_DIR"

# Sanity checks (remote)
ssh "$REMOTE" "cd '$REMOTE_DIR' >/dev/null 2>&1" || {
  echo "Remote dir not accessible: $REMOTE:$REMOTE_DIR" >&2
  exit 1
}

remote_find_cmd="cd '$REMOTE_DIR' && find database/ActorStat database/ReplayProStat -type f ! -newermt '$CUTOFF'"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[Dry-run] Matched files (mtime < $CUTOFF) count:" >&2
  ssh "$REMOTE" "$remote_find_cmd | wc -l"

  echo "[Dry-run] Matched files total size (approx):" >&2
  ssh "$REMOTE" "cd '$REMOTE_DIR' && find database/ActorStat database/ReplayProStat -type f ! -newermt '$CUTOFF' -printf '%s\n' 2>/dev/null | awk '{s+=\$1} END{printf \"%d bytes (%.3f GiB)\\n\", s, s/1024/1024/1024}'"

  echo "[Dry-run] Total directory sizes (NOT filtered; for reference):" >&2
  ssh "$REMOTE" "cd '$REMOTE_DIR' && du -sh database/ActorStat database/ReplayProStat 2>/dev/null || true"

  echo "[Dry-run] Newer-than-cutoff files count (sanity check):" >&2
  ssh "$REMOTE" "cd '$REMOTE_DIR' && find database/ActorStat database/ReplayProStat -type f -newermt '$CUTOFF' | wc -l"
  exit 0
fi

case "$MODE" in
  tar)
    # Stream archive to local; no remote temp files.
    # After successful extract, delete sources on remote.
    echo "[1/2] Streaming old files from $REMOTE:$REMOTE_DIR to $LOCAL_DIR ..." >&2
    if [[ "$COMPRESS" == "gzip" ]]; then
      ssh "$REMOTE" "cd '$REMOTE_DIR' && $remote_find_cmd -print0 | tar --null -T - -cf - | gzip -1" \
        | tar -xzf - -C "$LOCAL_DIR"
    else
      ssh "$REMOTE" "cd '$REMOTE_DIR' && $remote_find_cmd -print0 | tar --null -T - -cf -" \
        | tar -xf - -C "$LOCAL_DIR"
    fi

    if [[ "$DELETE_REMOTE" -eq 1 ]]; then
      echo "[2/2] Deleting matched old files on remote (explicit --delete-remote) ..." >&2
      ssh "$REMOTE" "cd '$REMOTE_DIR' && $remote_find_cmd -delete"
      echo "Done. Backup created under: $LOCAL_DIR ; Remote deleted." >&2
    else
      echo "Done. Backup created under: $LOCAL_DIR ; Remote NOT deleted (use --delete-remote to delete)." >&2
    fi
    ;;

  rsync)
    command -v rsync >/dev/null 2>&1 || {
      echo "Local rsync not found; install rsync or use --mode tar." >&2
      exit 1
    }
    ssh "$REMOTE" "command -v rsync >/dev/null 2>&1" || {
      echo "Remote rsync not found; install rsync on remote or use --mode tar." >&2
      exit 1
    }

    echo "[1/1] Pulling with rsync (will remove source files after each successful transfer)..." >&2
    # Pass a NUL-separated file list to rsync to avoid storing a giant list on remote.
    ssh "$REMOTE" "cd '$REMOTE_DIR' && $remote_find_cmd -print0" \
      | rsync -a --from0 --files-from=- --remove-source-files "$REMOTE:$REMOTE_DIR/" "$LOCAL_DIR/"

    # Remove now-empty directories (ignore errors)
    ssh "$REMOTE" "cd '$REMOTE_DIR' && find database/ActorStat database/ReplayProStat -type d -empty -delete" || true

    echo "Done. Backup created under: $LOCAL_DIR" >&2
    ;;

  *)
    echo "Unknown mode: $MODE (expected tar or rsync)" >&2
    exit 2
    ;;
esac
