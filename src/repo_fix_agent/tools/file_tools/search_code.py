from pathlib import Path

from .constants import MAX_FILE_SIZE
from .list_files import list_files
def search_code(repo_path: str, query: str, max_results: int = 20) -> list[str]:
    """
    Search repository files by filename and content, then return ranked paths.

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
    - Uses ``list_files(repo_path)`` for traversal, so the same repo filtering
      rules apply here.
    - Content search is skipped for files larger than ``MAX_FILE_SIZE``.
    - Unreadable files are ignored.
    """
    repo = Path(repo_path).resolve()
    query_lower = query.lower()
    matches: list[tuple[str, int]] = []

    for file_path in list_files(repo_path):
        full_path = repo / file_path
        score = 0

        if query_lower in file_path.lower():
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
            matches.append((file_path, score))

    matches.sort(key=lambda item: item[1], reverse=True)
    return [file_path for file_path, _ in matches[:max_results]]
