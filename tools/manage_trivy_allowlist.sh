#!/usr/bin/env bash
# Simple helper to manage the .trivyignore file.
set -euo pipefail

ACTION=${1:-list}
FILE=.trivyignore

case "$ACTION" in
  list)
    echo "Contents of $FILE:"
    nl -ba "$FILE" || true
    ;;
  add)
    shift || true
    for cve in "$@"; do
      if grep -qFx "$cve" "$FILE"; then
        echo "$cve already present"
      else
        echo "$cve" >> "$FILE"
        echo "Added $cve"
      fi
    done
    ;;
  remove)
    shift || true
    for cve in "$@"; do
      grep -vFx "$cve" "$FILE" > "$FILE.tmp" && mv "$FILE.tmp" "$FILE" || true
      echo "Removed $cve"
    done
    ;;
  *)
    echo "Usage: $0 [list|add|remove] [CVE...]"
    exit 2
    ;;
esac
