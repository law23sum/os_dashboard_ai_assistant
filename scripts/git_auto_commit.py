#!/usr/bin/env python3
"""Stage all changes and create a descriptive commit message automatically.

Usage:
    python scripts/git_auto_commit.py

The script stages everything (equivalent to `git add .`), inspects the staged
changes, generates a detailed commit message (including file list, stats, and a
rationale stub), and runs `git commit`. If nothing is staged after running,
it exits gracefully.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
REASONS_PATH = REPO_ROOT / ".git" / ".ai_stage_reasons.json"


def _run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        errors="replace",
    )


def _run_allow_fail(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        errors="replace",
    )


class GitStageError(RuntimeError):
    pass


def stage_everything() -> None:
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - error path
        msg = exc.stderr or exc.stdout or str(exc)
        raise GitStageError(msg.strip())


def staged_files() -> List[str]:
    proc = _run(["git", "diff", "--cached", "--name-only"])
    files = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return files


def diff_stat() -> str:
    proc = _run(["git", "diff", "--cached", "--stat"])
    return proc.stdout.strip()


def diff_full() -> str:
    proc = _run(["git", "diff", "--cached"])
    return proc.stdout.strip()


def get_branch() -> str:
    proc = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return proc.stdout.strip()


def build_commit_message(
    files: List[str],
    stat: str,
    ai_summary: Optional[str],
    summary_persona: str,
    file_reasons: Optional[Dict[str, str]] = None,
) -> str:
    timestamp = _dt.datetime.now(_dt.timezone.utc).isoformat()
    branch = get_branch()
    summary = f"Update {len(files)} file(s)"
    if files:
        summary += f" – {files[0]}" if len(files) == 1 else f" – {files[0]} & more"

    rationale = (
        "Automated summary: captures staged changes, including the updated files "
        "and execution context. Expand this section if additional reasoning is required."
    )

    body_lines = [
        "Summary:",
        f"- Files touched: {len(files)}",
        f"- Branch: {branch}",
        f"- Timestamp: {timestamp}",
        f"- Rationale: {rationale}",
        "",
    ]

    if file_reasons:
        body_lines.append("File Reasons:")
        preview_files = files[:10]
        for path in preview_files:
            reason = file_reasons.get(path, "(no reason captured)")
            body_lines.append(f"- {path}: {reason}")
        if len(files) > len(preview_files):
            body_lines.append(f"- … {len(files) - len(preview_files)} more file(s)")
        body_lines.append("")

    body_lines.append("Details:")
    if files:
        preview = files[:5]
        body_lines.extend(["- " + path for path in preview])
        if len(files) > len(preview):
            body_lines.append(f"- … {len(files) - len(preview)} more file(s)")
    else:
        body_lines.append("- No files detected (unexpected)")

    if ai_summary:
        body_lines.extend(["", f"AI Summary ({summary_persona}):", ai_summary.strip(), ""])

    if stat:
        body_lines.extend(["Diffstat:", stat])

    return summary + "\n\n" + "\n".join(body_lines)


def commit(message: str) -> int:
    proc = _run_allow_fail(["git", "commit", "-m", message])
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode or 0


def load_stage_reason_data() -> Dict:
    if not REASONS_PATH.exists():
        return {"files": {}}
    try:
        return json.loads(REASONS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"files": {}}


def save_stage_reason_data(data: Dict) -> None:
    REASONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    REASONS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def collect_file_reasons(files: List[str], data: Dict) -> Dict[str, str]:
    entries = data.get("files", {})
    reasons: Dict[str, str] = {}
    for path in files:
        entry = entries.get(path)
        if entry:
            reason = entry.get("reason")
            if reason:
                reasons[path] = reason
    return reasons


def clear_stage_reasons(files: List[str], data: Dict) -> None:
    entries = data.get("files", {})
    changed = False
    for path in files:
        if path in entries:
            del entries[path]
            changed = True
    if changed:
        data["files"] = entries
        save_stage_reason_data(data)


def edit_file_reasons(files: List[str], file_reasons: Dict[str, str], data: Dict) -> None:
    entries = data.setdefault("files", {})
    indexed = {str(i + 1): path for i, path in enumerate(files)}
    while True:
        print("\nFile reasons:")
        for idx, path in indexed.items():
            print(f"{idx}) {path}: {file_reasons.get(path, '(none)')}")
        selection = input("Enter number to edit (Enter to finish): ").strip()
        if not selection:
            save_stage_reason_data(data)
            return
        path = indexed.get(selection)
        if not path:
            print("Invalid selection.")
            continue
        current = file_reasons.get(path, "")
        new_reason = input(f"Reason for {path} [{current}]: ").strip()
        if not new_reason:
            new_reason = current or "Updated file."
        file_reasons[path] = new_reason
        entry = entries.setdefault(path, {})
        entry["reason"] = new_reason
        entry["source"] = "user"
        entry["updated_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()


def main() -> int:
    skip_stage = os.getenv("GIT_AUTO_SKIP_STAGE") == "1"
    if not skip_stage:
        try:
            stage_everything()
        except GitStageError as exc:
            print(
                "git add failed inside git_auto_commit.py. Make sure the repository is writable and .git/index isn't locked.\n"
                f"Details: {exc}",
                file=sys.stderr,
            )
            return 1
    else:
        print("Skipping staging step (controlled by GIT_AUTO_SKIP_STAGE).")
    files = staged_files()
    if not files:
        print("No staged changes detected. Nothing to commit.")
        return 0
    stat = diff_stat()
    diff_text = diff_full()
    persona = select_persona()
    ai_summary = generate_ai_summary(diff_text, persona=persona)
    stage_data = load_stage_reason_data()
    file_reasons = collect_file_reasons(files, stage_data)
    message = build_commit_message(files, stat, ai_summary, persona, file_reasons)
    message = interactive_review(
        message, ai_summary, diff_text, files, stat, persona, file_reasons, stage_data
    )
    if message is None:
        print("Commit aborted by user.")
        return 0
    result = commit(message)
    if result == 0:
        clear_stage_reasons(files, stage_data)
    return result


def generate_ai_summary(
    diff_text: str,
    instructions: Optional[str] = None,
    persona: str = "Chris",
) -> Optional[str]:
    if not diff_text:
        return None
    try:
        from assistant_core.ai import generate_ai_reply, openai_available
        from assistant_core.db import ChatMessage
    except Exception:  # pragma: no cover
        return None

    if not openai_available():
        return None

    base_prompt = (
        "You are AI OS's commit assistant. Given the staged git diff below, "
        "produce a concise summary (1-3 sentences) describing the intent, logic changes, "
        "and reasons. Focus on user-facing impact or architectural notes."
    )
    if instructions:
        base_prompt += f"\nAdditional instructions: {instructions.strip()}"
    prompt = base_prompt + "\nDiff:\n" + diff_text

    history = [
        ChatMessage(
            id="auto",
            persona="Chris",
            role="user",
            kind="chat",
            content="Summarize the upcoming commit.",
        )
    ]

    reply, error, _ = generate_ai_reply(
        history,
        persona=persona,
        prompt=prompt,
        append_prompt=False,
        fallback_prompt=prompt,
        system_prompt="You generate concise commit summaries for the AI OS repo.",
        enable_shell=False,
    )
    if error:
        sys.stderr.write(f"AI summary unavailable: {error}\n")
        return None
    return reply


def interactive_review(
    message: str,
    ai_summary: Optional[str],
    diff_text: str,
    files: List[str],
    stat: str,
    persona: str,
    file_reasons: Dict[str, str],
    stage_data: Dict,
) -> Optional[str]:
    while True:
        print("\n--- Proposed Commit Message ---\n")
        print(message)
        print("\n-------------------------------\n")
        choice = input(
            "[c]onfirm, [m]odify message, [d]ecline, [?] ask AI, [r]easons edit? "
        ).strip().lower()
        if choice in ("c", "", None):
            return message
        if choice == "d":
            return None
        if choice == "m":
            message = manual_edit(message)
            continue
        if choice == "?":
            instructions = input("Ask AI to refine the summary (or press Enter to cancel): ").strip()
            if not instructions:
                continue
            persona = select_persona(
                prompt="Persona to answer the question (press Enter to keep current)",
                default=persona,
            )
            new_summary = generate_ai_summary(diff_text, instructions, persona=persona)
            if not new_summary:
                print("AI summary unavailable. Keeping previous message.")
            else:
                ai_summary = new_summary
                message = build_commit_message(
                    files, stat, ai_summary, persona, file_reasons
                )
            continue
        if choice == "r":
            edit_file_reasons(files, file_reasons, stage_data)
            message = build_commit_message(
                files, stat, ai_summary, persona, file_reasons
            )
            continue
        print("Invalid choice. Please select c/m/d/?/r.")


def manual_edit(initial: str) -> str:
    editor = os.environ.get("EDITOR")
    if not editor:
        print("$EDITOR not set; enter commit message manually (Ctrl-D to finish). Current message shown below:\n")
        print(initial)
        print("\nEnter new commit message (or leave empty to use existing):")
        content = sys.stdin.read().strip()
        return content or initial

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write(initial)
        tmp_path = tmp.name
    try:
        subprocess.run(editor.split() + [tmp_path], check=True)
        with open(tmp_path, "r", encoding="utf-8") as handle:
            content = handle.read().strip()
        return content or initial
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def select_persona(prompt: str = "Select AI persona", default: str = "Chris") -> str:
    personas = ["Chris", "AIC", "Aria", "Sora"]
    prompt_text = f"{prompt} [{'/'.join(personas)}] (default {default}): "
    while True:
        choice = input(prompt_text).strip()
        if not choice:
            return default
        normalized = choice.capitalize()
        if normalized in personas:
            return normalized
        print("Unknown persona. Please choose from:", ", ".join(personas))


if __name__ == "__main__":
    raise SystemExit(main())
