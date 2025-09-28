Title: docs: archive old docs and add archive policy (docs/archive-cleanup-20250928)

Summary
-------
This PR archives older or duplicate documentation into `docs/archive/20250928/`, adds an `ARCHIVE_POLICY.md`, and restores placeholder pages to avoid broken links while maintainers decide canonical locations.

What I changed
---------------
- Added `docs/ARCHIVE_POLICY.md` (policy and rationale for archival)
- Moved multiple legacy/stale docs into `docs/archive/20250928/` (historical copies preserved)
- Created placeholder/redirect files to prevent broken links:
  - `docs/clinical/nurse_user_guide.md` (redirect/notice to archive)
  - `docs/developer_guide.md` (placeholder; archived copy at `docs/archive/20250928/developer_guide.bak`)
  - `docs/development/contributing.md` (placeholder)
  - `docs/development/setup-guide.md` (placeholder)
- Fixed several relative links in `docs/README.md` and updated the GitHub Issues URL

Why
---
The repository contained several duplicated and outdated documentation files. Archival keeps history while making the primary docs surface smaller and easier to maintain. Placeholders ensure existing links do not break and guide maintainers to restore canonical content when ready.

Validation
----------
- Ran a docs-only link check (excluding `docs/archive/`) and confirmed no missing internal Markdown links remain.
- Ran the test-suite locally with `AI_NURSE_DISABLE_REDIS=1` earlier during the cleanup; tests passed in that CI-like configuration.

Follow-ups / recommendations
---------------------------
- Decide canonical locations for the developer and contributing guides. If you want I can fully restore archived content into `docs/developer_guide.md` and `docs/development/contributing.md` instead of placeholders.
- Consider setting up a scheduled docs linter or link-check job in CI to prevent regressions.

Files moved to archive (high level)
---------------------------------
See `docs/archive/20250928/README.md` for a per-file map and rationale.

Notes
-----
This PR is intentionally conservative: it preserves archived content and creates lightweight placeholders so maintainers can review and merge without manual fixes to other files.
