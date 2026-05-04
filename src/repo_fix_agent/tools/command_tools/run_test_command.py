from pathlib import Path

from .helpers import normalize_command
from .is_test_command_allowed import is_test_command_allowed
from .models import CommandResult
from .run_command import run_command


def run_test_command(
    repo_path: str,
    command: str | list[str],
    timeout: int = 120,
) -> CommandResult:
    """Run a test/typecheck/lint command through safe executor."""
    cmd = normalize_command(command)

    if not is_test_command_allowed(cmd):
        return CommandResult(
            command=cmd,
            cwd=str(Path(repo_path).resolve()),
            returncode=-1,
            success=False,
            error="Test command is not allowed.",
        )

    return run_command(command=cmd, cwd=repo_path, timeout=timeout, check_allowed=True)
