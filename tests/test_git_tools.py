from __future__ import annotations

import subprocess
from pathlib import Path

from repo_fix_agent.tools.git_tools import (
    find_recent_or_changed_files,
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def test_find_recent_or_changed_files_reports_git_state(tmp_path: Path) -> None:
    repo = tmp_path
    _git(repo, "init")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")

    tracked = repo / "tracked.txt"
    tracked.write_text("v1\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "initial")

    tracked.write_text("v2\n", encoding="utf-8")
    staged = repo / "staged.txt"
    staged.write_text("stage me\n", encoding="utf-8")
    _git(repo, "add", "staged.txt")
    (repo / "untracked.txt").write_text("new file\n", encoding="utf-8")

    result = find_recent_or_changed_files(str(repo))

    assert "tracked.txt" in result["unstaged_files"]
    assert "staged.txt" in result["staged_files"]
    assert "untracked.txt" in result["untracked_files"]


def test_find_recent_or_changed_files_handles_non_git_directory(tmp_path: Path) -> None:
    result = find_recent_or_changed_files(str(tmp_path))

    assert result["is_git_repo"] is False
    assert result["errors"] == ["Not a git repository"]
