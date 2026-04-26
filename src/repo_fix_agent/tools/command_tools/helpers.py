import shlex


def normalize_command(command: str | list[str]) -> list[str]:
    if isinstance(command, str):
        return shlex.split(command)
    return command


def is_prefix(command: list[str], allowed_prefix: list[str]) -> bool:
    if len(command) < len(allowed_prefix):
        return False
    return command[: len(allowed_prefix)] == allowed_prefix
