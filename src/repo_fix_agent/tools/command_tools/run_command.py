import subprocess
from pathlib import Path

from .helpers import normalize_command
from .is_command_allowed import is_command_allowed
from .models import CommandResult


def run_command(
    command: str | list[str],
    cwd: str,
    timeout: int = 60,
    check_allowed: bool = True,
) -> CommandResult:
    """Safely run a shell command and return structured result."""
    cmd = normalize_command(command)
    repo = Path(cwd).resolve()

    if not repo.exists() or not repo.is_dir():
        return CommandResult(
            command=cmd,
            cwd=str(repo),
            stdout="",
            stderr="",
            returncode=-1,
            success=False,
            error=f"Invalid working directory: {repo}",
        )

    if check_allowed and not is_command_allowed(cmd):
        return CommandResult(
            command=cmd,
            cwd=str(repo),
            stdout="",
            stderr="",
            returncode=-1,
            success=False,
            error="Command is not allowed by safety policy.",
        )

    try:
        result = subprocess.run(
            cmd,
            cwd=repo,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            shell=False,
        )

        return CommandResult(
            command=cmd,
            cwd=str(repo),
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            success=result.returncode == 0,
        )

    except subprocess.TimeoutExpired as e:
        return CommandResult(
            command=cmd,
            cwd=str(repo),
            stdout=e.stdout or "",
            stderr=e.stderr or "",
            returncode=-1,
            success=False,
            timed_out=True,
            error=f"Command timed out after {timeout} seconds.",
        )

    except Exception as e:
        return CommandResult(
            command=cmd,
            cwd=str(repo),
            stdout="",
            stderr="",
            returncode=-1,
            success=False,
            error=str(e),
        )
