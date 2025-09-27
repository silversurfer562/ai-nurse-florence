ARCHIVE PLAN — Safe preview and archival for legacy/demo files

Purpose
-------
This document describes a safe, non-destructive workflow to identify, review, and archive legacy or duplicate files (for example: demo scripts, placeholder files, alternative app entry points). No files will be deleted without explicit approval.

Steps (preview only)
--------------------
1. Run the preview script to list candidates:

   ```bash
   ./scripts/preview_archive.sh
   ```

2. Review the output carefully. The script lists matching files and empty directories that look like leftovers.

Archival (manual, consent required)
----------------------------------
If you approve archiving, follow these steps (I can perform them for you after you confirm):

1. Create an `archive/legacy/<timestamp>/` directory in the repo root.
2. Move approved files/directories into that directory, preserving relative paths. Example:

   ```bash
   mkdir -p archive/legacy/2025-09-27
   git mv src/app_enhanced.py archive/legacy/2025-09-27/src_app_enhanced.py
   git mv artifacts/ archive/legacy/2025-09-27/artifacts
   ```

3. Commit the changes with a clear message: `git commit -m "archive: move legacy/demo files to archive/legacy/2025-09-27"`.

4. Optionally add a short README under the archive folder describing why each file was archived.

Notes and safeguards
--------------------
- Nothing is deleted by the preview script or this plan.
- Archival preserves git history for all moved files.
- I will not move files until you explicitly ask me to run the archival step.

Suggested next actions
----------------------
- Run `./scripts/preview_archive.sh` and paste the output here if you want me to review candidates and propose a precise list to archive.
- Or, say "archive approved for: <list>" and I'll perform the archival steps (moves + commit).
