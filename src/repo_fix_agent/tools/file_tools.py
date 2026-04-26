from pathlib import Path
import os
from typing import List, Any
import re

from langchain_core.tools import tool

# ---------------------------
# CONFIG (tune as needed)
# ---------------------------

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "coverage",
    ".next",
    ".turbo",
}

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".ico", ".pdf", ".zip", ".tar", ".gz",
    ".mp4", ".mp3", ".woff", ".woff2",
}

MAX_FILES = 1000
MAX_FILE_SIZE = 80 * 1024  # 80 KB

# ---------------------------
# list_files
# ---------------------------


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
    repo = Path(repo_path).resolve()
    results: List[str] = []

    for root, dirs, files in os.walk(repo):
        # Remove ignored directories in-place (important!)
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            file_path = Path(root) / file

            # Skip binary / irrelevant extensions
            if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                continue

            rel_path = file_path.relative_to(repo).as_posix()
            results.append(rel_path)

            if len(results) >= MAX_FILES:
                return results

    return results


# ---------------------------
# read_file
# ---------------------------

@tool
def read_file(repo_path: str, file_path: str) -> str:
    """
    Read a single file inside ``repo_path`` as UTF-8 text.

    Use this when the agent already knows which file to inspect.

    Args:
        repo_path: Absolute or relative path to the repository root.
        file_path: Path to the target file, relative to ``repo_path``.
            Example: ``"src/app/main.py"``.

    Behavior:
    - Prevents path traversal outside ``repo_path`` and raises ``ValueError``.
    - Raises ``FileNotFoundError`` if the file does not exist.
    - Reads with ``encoding="utf-8"`` and ``errors="ignore"``.
    - If the file is larger than ``MAX_FILE_SIZE``, returns the first
      ``MAX_FILE_SIZE`` characters followed by ``...[TRUNCATED]...``.
    """
    repo = Path(repo_path).resolve()
    if not repo.exists():
        raise ValueError(f"repo_path does not exist: {repo_path}")
    if not repo.is_dir():
        raise ValueError(f"repo_path is not a directory: {repo_path}")

    full_path = (repo / file_path).resolve()

    # Security: prevent path traversal
    try:
        full_path.relative_to(repo)
    except ValueError as exc:
        raise ValueError(
            f"file_path must stay inside repo_path: {file_path}"
        ) from exc

    if not full_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    size = full_path.stat().st_size

    if size > MAX_FILE_SIZE:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(MAX_FILE_SIZE)
        return content + "\n\n...[TRUNCATED]..."

    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# ---------------------------
# search_code
# ---------------------------


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

    repo = Path(repo_path).resolve()
    query_lower = query.lower()

    matches = []

    for file in list_files(repo_path):
        full_path = repo / file

        score = 0

        # Filename match (high signal)
        if query_lower in file.lower():
            score += 5

        try:
            # Skip large files for content search
            if full_path.stat().st_size <= MAX_FILE_SIZE:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    if query_lower in content.lower():
                        score += 2
        except Exception:
            continue

        if score > 0:
            matches.append((file, score))

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)

    return [file for file, _ in matches[:max_results]]


# ---------------------------
# grep_code
# ---------------------------


@tool
def grep_code(repo_path: str, pattern: str, max_results: int = 50) -> list[dict[str, Any]]:
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

    repo = Path(repo_path).resolve()
    regex = re.compile(pattern, re.IGNORECASE)

    results: list[dict[str, Any]] = []

    for file_path in list_files(repo_path):
        full_path = repo / file_path

        if full_path.suffix.lower() in IGNORE_EXTENSIONS:
            continue

        if full_path.stat().st_size > MAX_FILE_SIZE:
            continue

        try:
            content = read_file(repo_path, file_path)
        except Exception:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            if regex.search(line):
                results.append(
                    {
                        "file": file_path,
                        "line": line_number,
                        "match": line.strip(),
                    }
                )

                if len(results) >= max_results:
                    return results

    return results
