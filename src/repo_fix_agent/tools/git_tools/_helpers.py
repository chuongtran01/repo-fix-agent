from __future__ import annotations

from repo_fix_agent.tools.command_tools import run_git_command


def is_git_repo(repo_path: str) -> bool:
    """
    Check whether ``repo_path`` points to a valid Git working tree.

    Args:
        repo_path: Absolute or relative repository path to validate.

    Returns:
        ``True`` when ``repo_path`` is inside a Git work tree, otherwise ``False``.

    Notes:
        Uses ``git rev-parse --is-inside-work-tree`` through the internal
        ``run_git_command`` safety wrapper.
    """

    result = run_git_command(
        repo_path, ["rev-parse", "--is-inside-work-tree"])

    return result.returncode == 0 and result.stdout.strip() == "true"
