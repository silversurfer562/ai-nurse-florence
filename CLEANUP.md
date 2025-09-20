Summary of cleanup actions and safe next steps

What I did
- Added/expanded `.gitignore` to ignore archives (`*.zip`, `*.tgz`, `*.tar.gz`), backup folders, venvs, editor files, and common OS artifacts.
- Created a safe script `scripts/cleanup_archives.sh` that lists archive files under `/Users/patrickroebuck/Documents/code_local` (dry-run by default) and can move them to an `archives` folder when run with `--apply`.

Key findings
- Multiple large archive files and nested project copies were found under `Documents/code_local` (examples):
  - `/Users/patrickroebuck/Documents/code_local/AI-Nurse-Florence-before-overwrite.zip` (~72M)
  - `/Users/patrickroebuck/Documents/code_local/ai-nurse-florence-bak.zip` (~56M)
  - `/Users/patrickroebuck/Documents/code_local/ai-nurse-florence-clean.zip` (~49M)
  - `/Users/patrickroebuck/Documents/code_local/ai-nurse-florence-working-bak-9-17-25-7-15pm.zip` (~53M)
  - `/Users/patrickroebuck/Documents/code_local/ai-nurse-florence-working/` (directory, ~271M)

Why this matters
- Having backups, zips, and duplicate project copies inside or near the repo causes confusion and risks accidental commits of large binaries or stale code. The new `.gitignore` prevents new archives from being tracked; existing tracked files must be handled manually.

Safe recommended next steps (pick one)
1) Archive & remove duplicates (safe, reversible)
   - Run the script in apply mode to move archive files to a single outside folder:

```zsh
# dry-run (lists files)
bash scripts/cleanup_archives.sh

# actually move found archives to ../archives_from_cleanup
bash scripts/cleanup_archives.sh --apply --dest /Users/patrickroebuck/Documents/archives_from_cleanup
```

2) Consolidate the canonical working copy
   - Choose which directory is the single source of truth (likely `/Users/patrickroebuck/Documents/code_local/ai-nurse-florence-working/ai-nurse-florence`).
   - Create a git branch in the repo root and copy over only the necessary files (exclude `.venv`, node_modules, and other ignored items). Example safe sequence:

```zsh
# from repo root
git checkout -b consolidate-working-copy
rsync -av --exclude='.venv' --exclude='*.zip' --exclude='node_modules' /Users/patrickroebuck/Documents/code_local/ai-nurse-florence-working/ai-nurse-florence/ ./
git status
# inspect, run tests, then commit when ready
git add -A
git commit -m "Import canonical working copy"
```

3) Remove tracked archive files (if any were accidentally committed)
   - If some archives are already tracked in the repository, we can help remove them from Git history (careful: rewriting history). Recommend doing this only after agreeing on which files to purge.

Notes and assumptions
- I assumed the primary working code is the copy under `Documents/code_local/ai-nurse-florence-working/ai-nurse-florence` based on file lists; confirm if a different folder is canonical.
- I did not move or delete any user files without `--apply` from you.

Next steps I can take for you
- Run `scripts/cleanup_archives.sh --apply` to consolidate archives into `/Users/patrickroebuck/Documents/archives_from_cleanup`.
- Help copy and consolidate the canonical working copy into the repository root on a new git branch (non-destructive), run tests, and make a commit.
- Identify tracked large files and prepare a safe history-rewrite plan (if you want to remove blobs from Git history).

If you want me to proceed with any of the next steps, tell me which option and I'll execute it.
