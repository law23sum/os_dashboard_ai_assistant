# AGENTS

This repo includes a symlink named `Omniverse` that points to `/Users/sum/Desktop/Omniverse`.

Rules for the Omniverse folder (including the symlink target):
- Read-only by default. Do not write, modify, move, copy, or remove any files or folders.
- Exception: only proceed if the user explicitly includes the exact phrase "I grant permission to ..." and names the specific action and target.
- If the phrase is missing, remind the user and wait.

Journaling:
- Maintain `/Users/sum/Desktop/Omniverse/AI_JOURNAL.log`.
- Log every access to Omniverse files (read/write/move/copy/remove).
- Each entry should include an ISO-8601 timestamp, action, path, and brief purpose.
