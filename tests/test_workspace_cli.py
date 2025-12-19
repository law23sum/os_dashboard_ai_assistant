from pathlib import Path

from assistant_hub.ui.terminal.workspace import (
    RepoProfile,
    discover_git_repos,
    doctor_workspace,
    infer_repo_profile,
)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")


def test_discover_git_repos_respects_depth_and_git(tmp_path: Path) -> None:
    repo = tmp_path / "repo_a"
    deep_repo = tmp_path / "nested" / "repo_b"
    (repo / ".git").mkdir(parents=True)
    (deep_repo / ".git").mkdir(parents=True)

    shallow = discover_git_repos(tmp_path, max_depth=1)
    assert repo in shallow
    assert deep_repo not in shallow

    deeper = discover_git_repos(tmp_path, max_depth=3)
    assert deep_repo in deeper


def test_infer_repo_profile_detects_commands(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    _touch(tmp_path / "pyproject.toml")
    _touch(tmp_path / "requirements.txt")
    _touch(tmp_path / "package.json")
    _touch(tmp_path / "start_ui.py")
    (tmp_path / "frontend").mkdir()

    profile = infer_repo_profile(tmp_path)

    assert any("pytest" in cmd for cmd in profile.test_commands)
    assert any("npm test" in cmd for cmd in profile.test_commands)
    assert any("start_ui.py" in cmd or "dev:web" in cmd for cmd in profile.run_commands)
    assert profile.build_commands  # build commands inferred


def test_doctor_workspace_detects_missing_env_and_tests(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    profile = RepoProfile(path=repo, name="repo")
    notes = doctor_workspace([profile])
    assert any("env" in note for note in notes)
    assert any("tests" in note for note in notes)
