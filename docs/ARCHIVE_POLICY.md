# Documentation Archive Policy

This file describes the lightweight policy used to archive superseded or duplicate documentation in `docs/archive/`.

Purpose
- Keep the `docs/` tree focused on the canonical, actively-maintained documentation.
- Preserve historical or draft documents in `docs/archive/` so nothing is lost and reviewers can inspect prior content.

When to archive
- A document is duplicated and a canonical copy exists in `docs/` (archive the duplicate).
- A document is a TODO, placeholder, or incomplete and not required for immediate use (archive or mark clearly as TODO).
- Operational runbooks that are superseded by a consolidated `deployment.md` or `production-checklist.md` (archive the old ones).

Archive conventions
- Archived files are moved under `docs/archive/<YYYYMMDD>/` using `git mv` to preserve history.
- Each archive folder must contain a `README.md` describing why documents were archived.
- Do not delete archived files; they can be removed later by a separate cleanup effort once reviewers confirm.

Restoring archived docs
- To restore a file, use `git mv docs/archive/<date>/file.md docs/<desired-location>/file.md` and open a PR describing the restore reason.

Review & approval
- All archival moves should be performed on a feature branch and opened as a PR for maintainers to review.
- The PR should include a short list of moved files and the rationale recorded in the archive `README.md`.

Contact
- If you're not sure whether to archive a file, leave it in place and open an issue to discuss with the maintainers.

