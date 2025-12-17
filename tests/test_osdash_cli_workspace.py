import json
from types import SimpleNamespace
from pathlib import Path

from ui.terminal.commands.workspace import (
    handle_scan_command,
    handle_test_command,
    handle_doctor_command,
)


def _make_repo(base: Path, name: str = "repo") -> Path:
    repo = base / name
    (repo / ".git").mkdir(parents=True)
    return repo


def test_handle_scan_outputs_json(tmp_path, capsys) -> None:
    _make_repo(tmp_path)
    args = SimpleNamespace(root=str(tmp_path), max_depth=2, exclude=[], json=True)
    code = handle_scan_command(args)
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload[0]["name"] == "repo"


def test_handle_test_dry_run_lists_commands(tmp_path, capsys) -> None:
    repo = _make_repo(tmp_path)
    (repo / "requirements.txt").write_text("", encoding="utf-8")
    args = SimpleNamespace(
        root=str(tmp_path),
        max_depth=1,
        project=None,
        categories=["test"],
        autofix=False,
        dry_run=True,
    )
    code = handle_test_command(args)
    output = capsys.readouterr().out
    assert code == 0
    assert "pytest" in output


def test_handle_doctor_reports_notes(tmp_path, capsys) -> None:
    _make_repo(tmp_path)
    args = SimpleNamespace(root=str(tmp_path), max_depth=1, json=False)
    code = handle_doctor_command(args)
    output = capsys.readouterr().out
    assert code == 0
    assert "Doctor report" in output
