from pydantic import BaseModel


class CommandResult(BaseModel):
    command: list[str]
    cwd: str
    stdout: str = ""
    stderr: str = ""
    returncode: int
    success: bool
    timed_out: bool = False
    error: str | None = None
