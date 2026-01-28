#!/usr/bin/env python3
"""Opinionated macOS defensive hardening helper for the dashboard."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, List

OPS_ROOT = Path.home() / "OS_Dashboard_AI_Assistant"
LOG_DIR = OPS_ROOT / "logs"
OUTPUT_PATH = LOG_DIR / "macos_hardening.json"


def _run(cmd: List[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", f"{cmd[0]} not found"
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


@dataclass
class Control:
    name: str
    ok: bool
    evidence: str
    remediation: List[str]
    apply_commands: List[List[str]]


def firewall_control() -> Control:
    code, out, err = _run(
        ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"]
    )
    ok = code == 0 and "State = 1" in out
    remediation = [
        "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on",
        "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setblockall off",
    ]
    apply_cmds = [
        [
            "/usr/libexec/ApplicationFirewall/socketfilterfw",
            "--setglobalstate",
            "on",
        ],
        [
            "/usr/libexec/ApplicationFirewall/socketfilterfw",
            "--setblockall",
            "off",
        ],
    ]
    evidence = out or err or "unavailable"
    return Control("firewall_enabled", ok, evidence, remediation, apply_cmds)


def remote_login_control() -> Control:
    code, out, err = _run(["systemsetup", "-getremotelogin"])
    ok = code == 0 and "Off" in out
    remediation = ["sudo systemsetup -setremotelogin off"]
    apply_cmds = [["systemsetup", "-setremotelogin", "off"]]
    evidence = out or err or "unavailable"
    return Control("remote_login_disabled", ok, evidence, remediation, apply_cmds)


def filevault_control() -> Control:
    code, out, err = _run(["fdesetup", "status"])
    ok = code == 0 and "On" in out
    remediation = ["Open System Settings ▸ Privacy & Security ▸ FileVault ▸ Turn On"]
    return Control("filevault_enabled", ok, out or err or "unavailable", remediation, [])


def automatic_update_control() -> Control:
    code, out, err = _run(["softwareupdate", "--schedule"])
    ok = code == 0 and "on" in out.lower()
    remediation = ["sudo softwareupdate --schedule on"]
    apply_cmds = [["softwareupdate", "--schedule", "on"]]
    evidence = out or err or "unavailable"
    return Control("automatic_updates_enabled", ok, evidence, remediation, apply_cmds)


def gatekeeper_control() -> Control:
    code, out, err = _run(["spctl", "--status"])
    ok = code == 0 and "enabled" in out.lower()
    remediation = ["sudo spctl --master-enable"]
    apply_cmds = [["spctl", "--master-enable"]]
    return Control(
        "gatekeeper_enabled",
        ok,
        out or err or "unavailable",
        remediation,
        apply_cmds,
    )


def screensaver_control() -> Control:
    code_pw, out_pw, err_pw = _run(
        ["defaults", "-currentHost", "read", "com.apple.screensaver", "askForPassword"]
    )
    code_delay, out_delay, err_delay = _run(
        ["defaults", "read", "com.apple.screensaver", "askForPasswordDelay"]
    )
    ok_pw = code_pw == 0 and out_pw.strip() == "1"
    ok_delay = code_delay == 0 and out_delay.strip() in {"0", "0.0", "1"}
    ok = ok_pw and ok_delay
    remediation = [
        "defaults -currentHost write com.apple.screensaver askForPassword -int 1",
        "defaults write com.apple.screensaver askForPasswordDelay -int 0",
    ]
    apply_cmds = [
        [
            "defaults",
            "-currentHost",
            "write",
            "com.apple.screensaver",
            "askForPassword",
            "-int",
            "1",
        ],
        [
            "defaults",
            "write",
            "com.apple.screensaver",
            "askForPasswordDelay",
            "-int",
            "0",
        ],
    ]
    evidence = {
        "askForPassword": out_pw or err_pw or "unavailable",
        "askForPasswordDelay": out_delay or err_delay or "unavailable",
    }
    return Control("screensaver_password", ok, json.dumps(evidence), remediation, apply_cmds)


CONTROLS: List[Callable[[], Control]] = [
    firewall_control,
    remote_login_control,
    filevault_control,
    automatic_update_control,
    gatekeeper_control,
    screensaver_control,
]


def apply_required(controls: List[Control]) -> List[dict]:
    changes = []
    for control in controls:
        if control.ok or not control.apply_commands:
            continue
        for raw_cmd in control.apply_commands:
            code, out, err = _run(raw_cmd)
            changes.append(
                {
                    "control": control.name,
                    "command": " ".join(shlex.quote(part) for part in raw_cmd),
                    "returncode": code,
                    "stdout": out,
                    "stderr": err,
                }
            )
    return changes


def run_audit(apply: bool) -> dict:
    results = [control() for control in CONTROLS]
    applied: List[dict] = []
    if apply:
        applied = apply_required(results)
    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "hostname": os.uname().nodename,
        "controls": [asdict(item) for item in results],
        "applied": applied,
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit macOS defensive controls and optionally enable them."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Attempt to enable missing controls (requires sudo for some).",
    )
    args = parser.parse_args()
    summary = run_audit(args.apply)
    unhealthy = [ctrl for ctrl in summary["controls"] if not ctrl["ok"]]
    print(
        f"[macos_hardening] healthy={len(summary['controls']) - len(unhealthy)} "
        f"needs_attention={len(unhealthy)}"
    )
    for ctrl in unhealthy:
        print(f" - {ctrl['name']}: remediation -> {ctrl['remediation'][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
