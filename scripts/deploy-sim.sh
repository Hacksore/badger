#!/usr/bin/env bash
# Rsync app files into badgeware-simulator's root-badgeware (for ./go root).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=sync-common.sh
source "$SCRIPT_DIR/sync-common.sh"

if [[ ! -d "$BADGEWARE_SIM" ]]; then
  echo "error: BADGEWARE_SIM not found: $BADGEWARE_SIM" >&2
  echo "  Clone https://github.com/pimoroni/badgeware-simulator and set BADGEWARE_SIM in .env" >&2
  exit 1
fi

SIM_ABS="$(cd "$BADGEWARE_SIM" && pwd)"
DEST="$SIM_ABS/$SIM_ROOT/"

if [[ ! -d "$DEST" ]]; then
  echo "error: simulator root missing: $DEST" >&2
  echo "  Use a full badgeware-simulator checkout (main branch includes $SIM_ROOT/)." >&2
  exit 1
fi

echo "Sync: $SRC_PATH/ -> $DEST"
rsync "${RSYNC_OPTS[@]}" "${RSYNC_EXCLUDE[@]}" "$SRC_PATH/" "$DEST/"
echo "done. Run simulator: cd \"$SIM_ABS\" && ./go root"
