from .constants import ALLOWED_COMMAND_PREFIXES, BLOCKED_TOKENS
from .helpers import is_prefix, normalize_command


def is_command_allowed(command: str | list[str]) -> bool:
    """Return True when a command is allowed by safety policy."""
    cmd = normalize_command(command)
    if not cmd:
        return False

    command_text = " ".join(cmd).lower()
    for token in BLOCKED_TOKENS:
        if token in command_text:
            return False

    return any(is_prefix(cmd, allowed) for allowed in ALLOWED_COMMAND_PREFIXES)
