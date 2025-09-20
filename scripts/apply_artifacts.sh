#!/usr/bin/env bash
# Safe artifact application script
# Usage:
#  - Place your artifact files into ./artifacts/ (e.g. artifacts/config.py, artifacts/app.py)
#  - Run `bash scripts/apply_artifacts.sh` to preview what would change (dry-run)
#  - Run `bash scripts/apply_artifacts.sh --apply` to actually overwrite and backup files

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARTIFACTS_DIR="$REPO_ROOT/artifacts"
BACKUP_DIR="$REPO_ROOT/backups"
APPLY=0

usage() {
  cat <<EOF
Usage: $0 [--apply] [--help]
  --apply    Actually write artifacts to target files (default: dry-run)
  --help     Show this help

Places expected under: $ARTIFACTS_DIR
  - config artifact: artifacts/config.py  -> will be applied to utils/config.py
  - app artifact:    artifacts/app.py     -> will be applied to app.py

By default this script previews diffs and creates backups only when --apply is used.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

mkdir -p "$BACKUP_DIR"

apply_if_present() {
  local artifact="$1" target="$2"
  if [ ! -f "$artifact" ]; then
    echo "[skip] artifact not found: $artifact"
    return
  fi

  echo "\n--- Processing artifact: $artifact -> $target ---"

  if [ ! -f "$target" ]; then
    echo "[info] target does not exist, will create: $target"
  else
    echo "[info] showing diff (artifact -> current target)"
    diff -u "$target" "$artifact" || true
  fi

  if [ "$APPLY" -eq 1 ]; then
    ts=$(date +%Y%m%d-%H%M%S)
    backup_path="$BACKUP_DIR/$(basename $target).$ts.bak"
    if [ -f "$target" ]; then
      cp -v -- "$target" "$backup_path"
      echo "[backup] $target -> $backup_path"
    fi
    cp -v -- "$artifact" "$target"
    echo "[applied] $artifact -> $target"
  else
    echo "[dry-run] no changes made. Re-run with --apply to perform changes."
  fi
}

apply_if_present "$ARTIFACTS_DIR/config.py" "$REPO_ROOT/utils/config.py"
apply_if_present "$ARTIFACTS_DIR/app.py" "$REPO_ROOT/app.py"

echo "\nFinished. Backups (if any) are under: $BACKUP_DIR"
