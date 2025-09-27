#!/usr/bin/env bash
# Preview candidate legacy/duplicate files and directories for archival.
# This script only reports what would be archived; it does NOT delete or move anything.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "🔍 Archive preview — no changes will be made"
echo "Repository: $REPO_ROOT"
echo

## Patterns to consider archiving (safe defaults from ruff excludes and legacy names)
PATTERNS=(
  "src/app_enhanced.py"
  "src\\app_enhanced.py"
  "temp_app_fix.py"
  "api/*"
  "artifacts/*"
  "backups/*"
  "src/data/*"
)

echo "Candidate patterns:"
for p in "${PATTERNS[@]}"; do
  echo "  - $p"
done
echo

echo "Matching files and directories (preview):"
for p in "${PATTERNS[@]}"; do
  # Use bash glob expansion; fallback to find for patterns with ** or windows-style separators
  if compgen -G "$p" > /dev/null; then
    for f in $p; do
      if [ -e "$f" ]; then
        if [ -d "$f" ]; then
          echo "DIR : $f  — size: $(du -sh "$f" 2>/dev/null | cut -f1)"
        else
          echo "FILE: $f  — size: $(du -h "$f" 2>/dev/null | cut -f1)"
        fi
      fi
    done
  else
    # Use find for glob-like patterns
    find . -path "./${p#./}" -maxdepth 4 -print 2>/dev/null || true
  fi
done

echo
echo "Empty directories that look like leftovers (preview):"
find . -type d -empty ! -path "./.git/*" ! -path "./venv/*" ! -path "*/__pycache__*" | sed 's|./||' | while read -r dir; do
  echo "  Would archive (empty): $dir"
done

echo
echo "Summary: Review the list above. To archive files, run the steps in ARCHIVE_PLAN.md after you approve them."

exit 0
