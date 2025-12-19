#!/usr/bin/env python3
"""Interactive environment executor for OS Dashboard."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable or "python"


def ask_choice(prompt: str, options: Sequence[str], default: Optional[str] = None) -> str:
    opts = "/".join(options)
    default_text = f" [{default}]" if default else ""
    while True:
        answer = input(f"{prompt} ({opts}){default_text}: ").strip().lower()
        if not answer and default:
            return default
        if answer in options:
            return answer
        print(f"Please choose one of: {', '.join(options)}")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        answer = input(f"{prompt} {suffix}: ").strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer yes or no.")


@dataclass
class Step:
    label: str
    command: Sequence[str]
    cwd: Optional[Path] = None
    env_extra: Optional[Dict[str, str]] = None
    condition: Callable[[], bool] | None = None


def run_step(step: Step) -> bool:
    if step.condition and not step.condition():
        print(f"Skipping {step.label} (condition not met)")
        return True

    env = os.environ.copy()
    if step.env_extra:
        env.update(step.env_extra)

    print(f"\n→ {step.label}")
    print(f"   {shlex.join(step.command)}")
    try:
        result = subprocess.run(
            step.command,
            cwd=step.cwd or REPO_ROOT,
            env=env,
            check=False,
        )
    except FileNotFoundError as exc:
        print(f"   Failed: {exc}")
        return False

    if result.returncode != 0:
        print(f"   Failed with exit code {result.returncode}")
        return False
    return True


def maybe_copy_env(env_name: str, template: Path) -> None:
    target = REPO_ROOT / ".env"
    if target.exists():
        return
    if not template.exists():
        print(f"⚠️  No template found for {env_name} at {template}")
        return
    if ask_yes_no(f"Copy {template.name} to .env?"):
        target.write_text(template.read_text())
        print(f"Created .env from {template.name}")


def main() -> int:
    print("=== OS Dashboard Environment Executor ===")
    env_choice = ask_choice(
        "Select environment", ["dev", "alpha", "beta", "pre-prod", "prod"], default="dev"
    )

    env_templates = {
        "dev": "env.dev.example",
        "alpha": "env.alpha.example",
        "beta": "env.beta.example",
        "pre-prod": "env.preprod.example",
        "prod": "env.prod.example",
    }
    template_hint = env_templates.get(env_choice, "env.example")
    template_path = REPO_ROOT / template_hint
    print(f"Recommended env template: {template_hint}")
    maybe_copy_env(env_choice, template_path)

    steps: List[Step] = []

    if ask_yes_no("Install Python dependencies with pip install -r requirements.txt?", default=True):
        steps.append(
            Step(
                label="Install Python dependencies",
                command=[PYTHON, "-m", "pip", "install", "-r", "requirements.txt"],
            )
        )

    if ask_yes_no("Install package in editable mode (pip install -e .)?", default=True):
        steps.append(Step(label="Editable install", command=[PYTHON, "-m", "pip", "install", "-e", "."]))

    if ask_yes_no("Install frontend dependencies (npm install in frontend/)?", default=False):
        steps.append(Step(label="Install frontend deps", command=["npm", "install"], cwd=REPO_ROOT / "frontend"))

    run_backend = ask_yes_no("Run backend lint/build via harness now?", default=True)
    run_frontend = ask_yes_no("Run frontend build now?", default=False)
    run_tests = ask_yes_no("Run Python test suite (pytest tests/)?", default=False)

    if run_backend:
        steps.append(
            Step(
                label="Backend lint/build (osdash harness)",
                command=[PYTHON, "-m", "assistant_hub.ui.terminal.cli", "test", "--category", "lint", "--category", "build"],
                env_extra={"PYTHONPATH": str(REPO_ROOT / "src")},
            )
        )

    if run_frontend:
        steps.append(
            Step(
                label="Frontend build",
                command=["npm", "run", "build"],
                cwd=REPO_ROOT / "frontend",
            )
        )

    if run_tests:
        steps.append(
            Step(
                label="Python tests",
                command=[PYTHON, "-m", "pytest", "-q", "tests"],
                env_extra={"PYTHONPATH": str(REPO_ROOT / "src")},
            )
        )

    if ask_yes_no("Start docker-compose (default profile) after checks?", default=False):
        steps.append(Step(label="Docker compose up --build", command=["docker-compose", "up", "--build"]))

    if not steps:
        print("No steps selected. Exiting.")
        return 0

    print("\nPlanned steps:")
    for idx, step in enumerate(steps, start=1):
        cwd = f" (cwd={step.cwd})" if step.cwd else ""
        print(f" {idx}. {step.label}{cwd}")

    if not ask_yes_no("Proceed with execution?", default=True):
        print("Aborted by user.")
        return 0

    all_ok = True
    for step in steps:
        success = run_step(step)
        all_ok = all_ok and success

    print("\nDone." if all_ok else "\nFinished with failures.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
