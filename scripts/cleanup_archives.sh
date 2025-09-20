#!/usr/bin/env bash
# List archives and offer to move them to ../archives/ (dry-run by default)

set -euo pipefail

ROOT_DIR="/Users/patrickroebuck/Documents/code_local"
DEST_DIR="$ROOT_DIR/../archives_from_cleanup"
DRY_RUN=1

print_usage() {
  echo "Usage: $0 [--apply] [--dest DIR]"
  echo "  --apply    Actually move files instead of dry-run"
  echo "  --dest DIR Destination directory for moved archives (default: $DEST_DIR)"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) DRY_RUN=0; shift ;;
    --dest) DEST_DIR="$2"; shift 2 ;;
    -h|--help) print_usage; exit 0 ;;
    *) echo "Unknown arg: $1"; print_usage; exit 1 ;;
  esac
done

echo "Scanning for archives under: $ROOT_DIR"
mapfile -t FILES < <(find "$ROOT_DIR" -type f \( -iname "*.zip" -o -iname "*.tgz" -o -iname "*.tar.gz" -o -iname "*.tar" \) -print)

if [ ${#FILES[@]} -eq 0 ]; then
  echo "No archive files found under $ROOT_DIR"
  exit 0
fi

echo "Found ${#FILES[@]} archive(s):"
for f in "${FILES[@]}"; do
  ls -lh "$f" | awk '{print $5, $9}'
done

if [ "$DRY_RUN" -eq 1 ]; then
  echo "\nDry-run mode (no files moved). Run with --apply to move files to: $DEST_DIR"
  exit 0
fi

echo "Moving files to $DEST_DIR"
mkdir -p "$DEST_DIR"
for f in "${FILES[@]}"; do
  mv "$f" "$DEST_DIR/"
done
echo "Done. Moved ${#FILES[@]} files to $DEST_DIR"
