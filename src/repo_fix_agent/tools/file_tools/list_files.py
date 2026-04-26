from typing import List

from langchain_core.tools import tool

from ._helpers import iter_repo_files, resolve_repo
from .constants import IGNORE_EXTENSIONS, MAX_FILES


@tool
def list_files(repo_path: str) -> list[str]:
    """
    Recursively list candidate source files under ``repo_path``.

    Use this tool first to discover files the agent can inspect with ``read_file``.

    Args:
        repo_path: Absolute or relative path to the repository root.

    Returns:
        Relative POSIX-style file paths (e.g. ``src/repo_fix_agent/main.py``).
        The list may return early after ``MAX_FILES`` results.

    Filtering:
    - Skips directories listed in ``IGNORE_DIRS`` (e.g. ``.git``, ``node_modules``).
    - Skips files with extensions in ``IGNORE_EXTENSIONS`` (common binary/assets).
    """
    repo = resolve_repo(repo_path)
    results: List[str] = []

    for file_path in iter_repo_files(repo):
        if file_path.suffix.lower() in IGNORE_EXTENSIONS:
            continue
        rel_path = file_path.relative_to(repo).as_posix()
        results.append(rel_path)
        if len(results) >= MAX_FILES:
            return results

    return results
