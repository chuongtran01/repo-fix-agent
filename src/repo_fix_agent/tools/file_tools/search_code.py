from pathlib import Path
from typing import List

from langchain_core.tools import tool

from ._helpers import resolve_repo
from .constants import MAX_FILE_SIZE
from .list_files import list_files


@tool
def search_code(repo_path: str, query: str, max_results: int = 20) -> List[str]:
    """
    Search repository files by filename and content, then return ranked matches.

    Args:
        repo_path: Absolute or relative path to the repository root.
        query: Search text to match against file paths and file contents
            (case-insensitive).
        max_results: Maximum number of matched file paths to return.

    Returns:
        A list of relative file paths ranked by a simple relevance score:
        - +5 if ``query`` appears in the file path/name
        - +2 if ``query`` appears in file content

    Notes:
    - Uses ``list_files(repo_path)`` for traversal, so directory/file filtering
      from that tool applies.
    - Content search is skipped for files larger than ``MAX_FILE_SIZE``.
    - Unreadable files are ignored.
    """
    repo = resolve_repo(repo_path)
    query_lower = query.lower()
    matches: list[tuple[str, int]] = []

    for file in list_files.func(repo_path):
        full_path = Path(repo) / file
        score = 0

        if query_lower in file.lower():
            score += 5

        try:
            if full_path.stat().st_size <= MAX_FILE_SIZE:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if query_lower in content.lower():
                    score += 2
        except Exception:
            continue

        if score > 0:
            matches.append((file, score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return [file for file, _ in matches[:max_results]]
