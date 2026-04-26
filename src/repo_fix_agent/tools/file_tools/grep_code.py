import re
from typing import Any

from langchain_core.tools import tool

from ._helpers import resolve_repo
from .constants import IGNORE_EXTENSIONS, MAX_FILE_SIZE
from .list_files import list_files
from .models import GrepCodeMatch


@tool
def grep_code(
    repo_path: str, pattern: str, max_results: int = 50
) -> list[dict[str, Any]]:
    """
    Run a regex search across repository text files and return line-level matches.

    Args:
        repo_path: Absolute or relative path to the repository root.
        pattern: Regular expression pattern (compiled with ``re.IGNORECASE``).
        max_results: Maximum number of matched lines to return.

    Returns:
        A list of match records with this shape:
        ``{"file": <relative_path>, "line": <1-based line number>, "match": <line text>}``.

    Notes:
        - File candidates come from ``list_files(repo_path)``.
        - Files above ``MAX_FILE_SIZE`` are skipped.
        - Unreadable files and invalid reads are ignored.
        - Returns early once ``max_results`` matches are collected.
    """
    repo = resolve_repo(repo_path)
    regex = re.compile(pattern, re.IGNORECASE)
    results: list[dict[str, Any]] = []

    for file_path in list_files.func(repo_path):
        full_path = repo / file_path
        if full_path.suffix.lower() in IGNORE_EXTENSIONS:
            continue
        if full_path.stat().st_size > MAX_FILE_SIZE:
            continue

        try:
            content = full_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            if regex.search(line):
                match = GrepCodeMatch(
                    file=file_path,
                    line=line_number,
                    match=line.strip(),
                )
                results.append(match.model_dump())
                if len(results) >= max_results:
                    return results
    return results
