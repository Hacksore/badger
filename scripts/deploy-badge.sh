#!/usr/bin/env bash
# Rsync app files from this repo to the mounted badge USB volume.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=sync-common.sh
source "$SCRIPT_DIR/sync-common.sh"

DEST="${BADGER_MOUNT%/}/"

if [[ ! -d "$BADGER_MOUNT" ]]; then
  echo "error: badge not mounted at $BADGER_MOUNT" >&2
  exit 1
fi

echo "Sync: $SRC_PATH/ -> $DEST"
rsync "${RSYNC_OPTS[@]}" "${RSYNC_EXCLUDE[@]}" "$SRC_PATH/" "$DEST/"
sync
echo "done."
