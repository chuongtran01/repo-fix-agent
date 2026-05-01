from ._helpers import iter_repo_files, resolve_repo, should_skip_path
from .constants import MAX_FILES

def list_files(repo_path: str) -> list[str]:
    """
    Recursively list candidate repo files under ``repo_path``.

    Args:
        repo_path: Absolute or relative path to the repository root.

    Returns:
        Relative POSIX-style file paths (e.g. ``src/repo_fix_agent/main.py``).
        The list may return early after ``MAX_FILES`` results.

    Filtering:
    - Skips directories listed in ``IGNORE_DIRS`` (for example ``.git`` and
      ``node_modules``).
    - Skips files with extensions in ``IGNORE_EXTENSIONS`` (common binary/assets).
    """
    repo = resolve_repo(repo_path)
    results: list[str] = []

    for file_path in iter_repo_files(repo):
        if should_skip_path(file_path):
            continue
        results.append(file_path.relative_to(repo).as_posix())
        if len(results) >= MAX_FILES:
            return results

    return results
