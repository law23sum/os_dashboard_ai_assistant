from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import assistant_hub.ui.terminal.harness as harness
from assistant_hub.ui.terminal.harness import (
    CheckResult,
    detect_project_profile,
    latest_workspace_report,
    run_checks,
    run_workspace_checks,
    write_report,
    write_workspace_report,
)


def test_detect_project_profile_infers_commands(tmp_path: Path) -> None:
    """Ensure both Python and frontend commands are detected when present."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "requirements.txt").write_text("")

    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        json.dumps({"name": "demo", "scripts": {"test": "npm test", "lint": "npm run lint"}}),
        encoding="utf-8",
    )

    profile = detect_project_profile(tmp_path)
    assert "test" in profile.commands
    assert any("pytest" in cmd for cmd in profile.commands["test"][0])
    assert any(cmd[0] == "npm" for cmd in profile.commands["test"])


def test_run_checks_and_report(tmp_path: Path, monkeypatch) -> None:
    """Smoke test the harness runner and report writer."""
    monkeypatch.setenv("OSDASH_HARNESS_LOG_DIR", str(tmp_path))
    (tmp_path / ".git").mkdir()
    profile = detect_project_profile(tmp_path)
    profile.commands = {"test": [[sys.executable, "-c", "import sys; sys.exit(0)"]]}

    explicit_run_id = "test-run-id"
    results = run_checks(profile, ["test"], autofix=False, run_id=explicit_run_id)
    assert results and results[0].status == "passed"
    assert results[0].run_id == explicit_run_id

    report_path = write_report(profile, results)
    saved = json.loads(report_path.read_text())
    assert saved["profile"]["name"] == profile.name
    assert saved["summary"]["run_id"] == explicit_run_id


def test_run_checks_respects_timeout(tmp_path: Path) -> None:
    """Commands that exceed timeout should fail quickly with an error note."""
    (tmp_path / ".git").mkdir()
    profile = detect_project_profile(tmp_path)
    profile.commands = {"test": [[sys.executable, "-c", "import time; time.sleep(2)"]]}

    results = run_checks(profile, ["test"], run_id="timeout-test", timeout_seconds=1)
    assert results and results[0].status == "failed"
    assert results[0].error and "timeout" in results[0].error


def test_write_workspace_report_collects_failures(tmp_path: Path, monkeypatch) -> None:
    """Aggregate reports across projects and capture errors."""
    monkeypatch.setenv("OSDASH_HARNESS_LOG_DIR", str(tmp_path))
    (tmp_path / ".git").mkdir()
    profile = detect_project_profile(tmp_path)
    success = run_checks(profile, ["test"], autofix=False)
    failing_result = [
        CheckResult(
            category="lint",
            command=["python", "-c", "exit(1)"],
            status="failed",
            exit_code=1,
            duration_seconds=0.01,
            output="lint failed",
            ran_at=0.0,
            run_id="test-run",
            timeout_seconds=5,
        )
    ]

    report_path = write_workspace_report(tmp_path, [(profile, success + failing_result)])
    payload = json.loads(report_path.read_text())

    assert payload["summary"]["projects"] == 1
    assert payload["summary"]["failed"] == 1
    assert payload["errors"] and payload["errors"][0]["project"] == profile.name


def test_run_workspace_checks_dry_run(monkeypatch, tmp_path: Path) -> None:
    """Dry runs should plan commands without executing them and persist a report."""

    profile = detect_project_profile(tmp_path)
    profile.commands = {"lint": [["echo", "lint"]]}

    monkeypatch.setattr(harness, "discover_profiles", lambda base, max_depth=2: [profile])

    report = run_workspace_checks(tmp_path, ["lint"], dry_run=True, report_path=tmp_path / "report.json")
    assert report["summary"]["skipped"] == 1
    assert report["summary"]["failed"] == 0
    report_path = Path(report["summary"]["report_path"])
    assert report_path.exists()


def test_run_workspace_checks_executes(monkeypatch, tmp_path: Path) -> None:
    """Non-dry runs should execute commands and capture pass/fail counts."""

    profile = detect_project_profile(tmp_path)
    profile.commands = {"test": [[sys.executable, "-c", "import sys; sys.exit(0)"]]}

    monkeypatch.setattr(harness, "discover_profiles", lambda base, max_depth=2: [profile])

    report = run_workspace_checks(tmp_path, ["test"], dry_run=False, timeout_seconds=2)
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 0


def test_latest_workspace_report_finds_recent(monkeypatch, tmp_path: Path) -> None:
    """latest_workspace_report should surface the newest aggregated output."""

    report_dir = tmp_path / "logs"
    monkeypatch.setenv("OSDASH_HARNESS_LOG_DIR", str(report_dir))

    profile = detect_project_profile(tmp_path)
    profile.commands = {}

    result = CheckResult(
        category="test",
        command=["echo", "ok"],
        status="passed",
        exit_code=0,
        duration_seconds=0.01,
        output="ok",
        ran_at=time.time(),
        run_id="unit-test",
        timeout_seconds=5,
    )

    write_workspace_report(tmp_path, [(profile, [result])])
    loaded = latest_workspace_report(report_dir)

    assert loaded is not None
    assert loaded.get("summary", {}).get("status") == "passed"
    assert loaded.get("report_path")
