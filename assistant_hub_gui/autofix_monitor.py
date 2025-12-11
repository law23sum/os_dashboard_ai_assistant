"""Shared helpers to launch the AI auto-fix monitor across entry points."""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TextIO, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
_AUTOFIX_DISABLE_ENV = "OSDASH_DISABLE_AUTOFIX"
_AUTOFIX_CONSOLE_ENV = "OSDASH_AUTOFIX_CONSOLE"
_AUTOFIX_LOG = REPO_ROOT / "logs" / "auto_fix" / "monitor.log"
_AUTOFIX_PREFIX = "[auto-fix]"


@dataclass
class AutoFixMonitor:
    process: subprocess.Popen
    log_handle: TextIO
    pump_thread: Optional[threading.Thread]
    console_proc: Optional[subprocess.Popen]


def _launch_auto_fix_console(log_path: Path) -> Tuple[Optional[subprocess.Popen], bool]:
    """Open a platform-specific terminal window that tails the auto-fix log."""
    quoted_log = shlex.quote(str(log_path))
    quoted_root = shlex.quote(str(REPO_ROOT))
    tail_cmd = f"cd {quoted_root} && tail -n 200 -f {quoted_log}"

    if sys.platform == "darwin":
        script = f'''
tell application "Terminal"
    activate
    do script "{tail_cmd}"
end tell
'''
        try:
            subprocess.Popen(["osascript", "-e", script])
            return None, True
        except Exception:
            return None, False

    if os.name == "nt":
        ps_cmd = f"Get-Content -Path '{str(log_path)}' -Wait"
        full_cmd = f"powershell -NoExit {ps_cmd}"
        try:
            proc = subprocess.Popen(
                ["cmd.exe", "/k", full_cmd],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            return proc, True
        except Exception:
            return None, False

    terminals = []
    if shutil.which("gnome-terminal"):
        terminals.append(["gnome-terminal", "--", "bash", "-lc", f"{tail_cmd}"])
    if shutil.which("xterm"):
        terminals.append(
            ["xterm", "-T", "Auto Fix Monitor", "-hold", "-e", "bash", "-lc", tail_cmd]
        )
    if shutil.which("konsole"):
        terminals.append(["konsole", "-e", "bash", "-lc", tail_cmd])

    for command in terminals:
        try:
            return subprocess.Popen(command), True
        except Exception:
            continue

    return None, False


def _should_use_external_console(preference: Optional[str] = None) -> bool:
    pref = preference or os.environ.get(_AUTOFIX_CONSOLE_ENV, "external")
    pref = pref.strip().lower()
    return pref in {"external", "window", "terminal"}


def start_auto_fix_monitor(
    *, inline_override: Optional[bool] = None
) -> Optional[AutoFixMonitor]:
    """Start the AI auto-fix watchdog in the background."""
    if os.environ.get(_AUTOFIX_DISABLE_ENV, "").lower() in {"1", "true", "yes"}:
        print("[launcher] Auto-fix monitor disabled via environment override.")
        return None

    script_path = REPO_ROOT / "scripts" / "ai_auto_fix.py"
    if not script_path.exists():
        return None

    _AUTOFIX_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_handle = _AUTOFIX_LOG.open("a", encoding="utf-8")
    log_handle.write("\n=== auto-fix monitor starting ===\n")
    log_handle.flush()

    cmd = [
        sys.executable,
        str(script_path),
        "--backend",
        "none",
        "--frontend",
        "none",
        "--logs-only",
        "--daemon",
    ]
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )

        use_inline = inline_override
        if use_inline is None:
            use_inline = not _should_use_external_console()

        console_proc: Optional[subprocess.Popen] = None
        console_opened = False
        if not use_inline:
            console_proc, console_opened = _launch_auto_fix_console(_AUTOFIX_LOG)
            use_inline = not console_opened

        def _pump_output() -> None:
            assert proc.stdout is not None
            for raw in proc.stdout:
                if raw is None:
                    break
                line = raw.rstrip("\n")
                log_handle.write(line + "\n")
                log_handle.flush()
                if use_inline and line:
                    print(f"{_AUTOFIX_PREFIX} {line}")
            proc.stdout.close()

        thread = threading.Thread(target=_pump_output, name="auto-fix-pump", daemon=True)
        thread.start()

        if use_inline:
            print("[launcher] Auto-fix monitor streaming to this terminal.")
        elif console_opened:
            print("[launcher] Auto-fix monitor console opened.")
        else:
            print("[launcher] Auto-fix monitor output will appear once console opens.")

        return AutoFixMonitor(proc, log_handle, thread, console_proc)
    except Exception as exc:
        print(f"[launcher] Warning: could not start auto-fix monitor ({exc}).")
        log_handle.write(f"auto-fix launch failed: {exc}\n")
        log_handle.close()
        return None


def stop_auto_fix_monitor(monitor: Optional[AutoFixMonitor]) -> None:
    """Stop the auto-fix watchdog and clean up resources."""
    if not monitor:
        return
    proc = monitor.process
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    if monitor.pump_thread and monitor.pump_thread.is_alive():
        monitor.pump_thread.join(timeout=2)
    monitor.log_handle.write("=== auto-fix monitor stopped ===\n")
    monitor.log_handle.close()
    console_proc = monitor.console_proc
    if console_proc and console_proc.poll() is None:
        try:
            console_proc.terminate()
        except Exception:
            pass


__all__ = ["AutoFixMonitor", "start_auto_fix_monitor", "stop_auto_fix_monitor"]
