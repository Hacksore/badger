#!/usr/bin/env bash
# Shared config for deploy-badge.sh and deploy-sim.sh (source this file, do not execute).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$REPO_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$REPO_ROOT/.env"
  set +a
fi

BADGER_MOUNT="${BADGER_MOUNT:-/Volumes/BADGER}"
BADGEWARE_SIM="${BADGEWARE_SIM:-$REPO_ROOT/../badgeware-simulator}"
BADGE_SRC="${BADGE_SRC:-.}"
SIM_ROOT="${SIM_ROOT:-root-badgeware}"

SRC_PATH="$(cd "$REPO_ROOT/$BADGE_SRC" && pwd)"

RSYNC_OPTS=(-a -v)
if [[ "${SYNC_DELETE:-0}" == "1" ]]; then
  RSYNC_OPTS+=(--delete)
fi

RSYNC_EXCLUDE=()
if [[ -f "$REPO_ROOT/.badgeignore" ]]; then
  RSYNC_EXCLUDE+=(--exclude-from="$REPO_ROOT/.badgeignore")
fi
