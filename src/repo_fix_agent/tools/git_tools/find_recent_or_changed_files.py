from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from repo_fix_agent.tools.command_tools import run_git_command
from repo_fix_agent.tools.git_tools._helpers import is_git_repo
from repo_fix_agent.tools.git_tools.models import FindRecentOrChangedFilesResult


@tool
def find_recent_or_changed_files(
    repo_path: str,
    recent_limit: int = 20,
    changed_limit: int = 50,
) -> dict[str, Any]:
    """
    Collect Git file context useful for planning and debugging agent actions.

    The tool gathers:
    - currently staged files
    - currently unstaged files
    - untracked files
    - recently touched files from Git history

    Args:
        repo_path: Repository root path.
        recent_limit: Number of recent commits to scan for ``recent_files``.
        changed_limit: Maximum number of files returned per changed-file bucket
            (staged, unstaged, untracked).

    Returns:
        A dictionary with the shape:
        - ``is_git_repo`` (bool): Whether the path is a Git repository.
        - ``changed_files`` (list[str]): Deduplicated union of staged/unstaged/untracked.
        - ``staged_files`` (list[str]): Paths from ``git diff --cached --name-only``.
        - ``unstaged_files`` (list[str]): Paths from ``git diff --name-only``.
        - ``untracked_files`` (list[str]): Paths from ``git ls-files --others --exclude-standard``.
        - ``recent_files`` (list[str]): Unique file paths from recent commit history.
        - ``errors`` (list[str]): Non-empty command errors collected during execution.

    Behavior:
        If ``repo_path`` is not a Git repository, returns empty file lists and
        ``errors=["Not a git repository"]``.
    """

    errors: list[str] = []

    if not is_git_repo(repo_path):
        return FindRecentOrChangedFilesResult(
            is_git_repo=False,
            changed_files=[],
            staged_files=[],
            unstaged_files=[],
            untracked_files=[],
            recent_files=[],
            errors=["Not a git repository"],
        ).model_dump()

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

    changed_files = sorted(
        set(staged_files + unstaged_files + untracked_files)
    )

    return FindRecentOrChangedFilesResult(
        is_git_repo=True,
        changed_files=changed_files,
        staged_files=staged_files,
        unstaged_files=unstaged_files,
        untracked_files=untracked_files,
        recent_files=recent_files,
        errors=[e for e in errors if e],
    ).model_dump()
