from pathlib import Path
from typing import Literal

from .constants import READONLY_GIT_COMMANDS, SAFE_WRITE_GIT_COMMANDS
from .models import CommandResult
from .run_command import run_command


def run_git_command(
    repo_path: str,
    args: list[str],
    timeout: int = 30,
    mode: Literal["readonly", "safe-write"] = "readonly",
) -> CommandResult:
    """Run a git command with readonly/safe-write policy."""
    if not args:
        return CommandResult(
            command=["git"],
            cwd=str(Path(repo_path).resolve()),
            returncode=-1,
            success=False,
            error="Missing git arguments.",
        )

    git_subcommand = args[0]

    if git_subcommand in READONLY_GIT_COMMANDS:
        return run_command(
            command=["git", *args],
            cwd=repo_path,
            timeout=timeout,
            check_allowed=True,
        )

    if mode == "safe-write" and git_subcommand in SAFE_WRITE_GIT_COMMANDS:
        if git_subcommand == "checkout" and "--" not in args:
            return CommandResult(
                command=["git", *args],
                cwd=str(Path(repo_path).resolve()),
                returncode=-1,
                success=False,
                error="Only file checkout with `git checkout -- <path>` is allowed.",
            )

        return run_command(
            command=["git", *args],
            cwd=repo_path,
            timeout=timeout,
            check_allowed=False,
        )

    return CommandResult(
        command=["git", *args],
        cwd=str(Path(repo_path).resolve()),
        returncode=-1,
        success=False,
        error=f"Git command not allowed: git {' '.join(args)}",
    )
