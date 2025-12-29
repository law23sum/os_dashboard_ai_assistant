# Workspace Scan (Desktop / Documents / Downloads)

## Documents (Sensitive/Permanent)
- Structure is category-based (Business, Employment, Financial, Health, Insurance, Legal, Personal, etc.).
- Each folder title is Title Case and singular, matching the "permanent record" rule. Recommend keeping this as canonical storage for completed paperwork.

## Desktop (Active Interactions)
- Mix of verb-focused queues (`01_Inbox`, `02_Active`, `Prepare`, `Read`, `Sort (Organize)`) and topic folders (`Employment`, `Financial`, `Taxes`).
- Windows artifacts (`$RECYCLE.BIN`, `desktop.ini`, `Thumbs.db`) were cluttering the root; they’ve been archived under `Desktop/99_Archive/SystemArtifacts/`.
- Suggestion: keep only in-progress material here; once a folder is finalized (e.g., `Financial` statements filed) move to the parallel folder under Documents to stay compliant with your rule.

## Downloads (Needs Organization)
- Contains installers, datasets, media bundles, and numerous project exports.
- Added structure under `Downloads/_archive`:
  - `photos/` – holds 12 photo ZIP archives that were previously loose.
  - `installers/chromedriver/` – now houses chromedriver installers and duplicate extractions; the freshest build lives in `Downloads/_incoming/installers/` for easy access.
- Remaining clutter (budgets, trade-exchange archives, large CSVs) is documented in `logs/user_attention.md` for your review.

## Logs
- `logs/move_log.csv` tracks every relocation (timestamp, source, destination, reason).
- `logs/user_attention.md` lists items awaiting your decision.

