from .constants import ALLOWED_TEST_PREFIXES
from .helpers import is_prefix, normalize_command


def is_test_command_allowed(command: str | list[str]) -> bool:
    """Return True when a command is allowed by the test-only safety policy."""
    cmd = normalize_command(command)
    if not cmd:
        return False

    return any(is_prefix(cmd, allowed) for allowed in ALLOWED_TEST_PREFIXES)
