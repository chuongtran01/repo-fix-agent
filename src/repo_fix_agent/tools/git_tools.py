# src/repo_fix_agent/tools/git_tools.py

from __future__ import annotations

from pathlib import Path
from typing import Any

from repo_fix_agent.tools.command_tools import run_git_command
from langchain_core.tools import tool


@tool
def is_git_repo(repo_path: str) -> bool:
    """
        Returns True if repo_path is inside a git repository.
        """

    result = run_git_command(
        repo_path, ["rev-parse", "--is-inside-work-tree"])

    return result.returncode == 0 and result.stdout.strip() == "true"


@tool
def find_recent_or_changed_files(
    repo_path: str,
    recent_limit: int = 20,
    changed_limit: int = 50,
) -> dict[str, Any]:
    """
    Uses git commands (via command_tools) to find:
    - staged files
    - unstaged files
    - untracked files
    - recently modified files (from git history)

    Returns structured result.
    """

    errors: list[str] = []

    # ---------------------------
    # Check if git repo
    # ---------------------------

    if not is_git_repo(repo_path):
        return {
            "is_git_repo": False,
            "changed_files": [],
            "staged_files": [],
            "unstaged_files": [],
            "untracked_files": [],
            "recent_files": [],
            "errors": ["Not a git repository"],
        }

    # ---------------------------
    # Staged files
    # ---------------------------
    staged_result = run_git_command(
        repo_path, ["diff", "--cached", "--name-only"])

    staged_files = []
    if staged_result.success:
        staged_files = [
            line.strip()
            for line in staged_result.stdout.splitlines()
            if line.strip()
        ][:changed_limit]
    else:
        errors.append(staged_result.stderr or staged_result.error or "")

    # ---------------------------
    # Unstaged files
    # ---------------------------
    unstaged_result = run_git_command(repo_path, ["diff", "--name-only"])

    unstaged_files = []
    if unstaged_result.success:
        unstaged_files = [
            line.strip()
            for line in unstaged_result.stdout.splitlines()
            if line.strip()
        ][:changed_limit]
    else:
        errors.append(unstaged_result.stderr or unstaged_result.error or "")

    # ---------------------------
    # Untracked files
    # ---------------------------
    untracked_result = run_git_command(
        repo_path,
        ["ls-files", "--others", "--exclude-standard"],
    )

    untracked_files = []
    if untracked_result.success:
        untracked_files = [
            line.strip()
            for line in untracked_result.stdout.splitlines()
            if line.strip()
        ][:changed_limit]
    else:
        errors.append(untracked_result.stderr or untracked_result.error or "")

    # ---------------------------
    # Recently touched files (git history)
    # ---------------------------
    recent_result = run_git_command(
        repo_path,
        [
            "log",
            "--name-only",
            "--pretty=format:",
            f"-n{recent_limit}",
        ],
    )

    recent_files: list[str] = []
    if recent_result.success:
        seen = set()

        for line in recent_result.stdout.splitlines():
            file_path = line.strip()

            if not file_path:
                continue

            if file_path not in seen:
                seen.add(file_path)
                recent_files.append(file_path)
    else:
        errors.append(recent_result.stderr or recent_result.error or "")

    # ---------------------------
    # Combine changed files
    # ---------------------------
    changed_files = sorted(
        set(staged_files + unstaged_files + untracked_files)
    )

    return {
        "is_git_repo": True,
        "changed_files": changed_files,
        "staged_files": staged_files,
        "unstaged_files": unstaged_files,
        "untracked_files": untracked_files,
        "recent_files": recent_files,
        "errors": [e for e in errors if e],
    }
