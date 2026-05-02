from ._helpers import resolve_repo


def read_file(
    repo_path: str,
    file_path: str,
    *,
    max_chars: int | None = None,
) -> str:
    """
    Read one file inside ``repo_path`` as UTF-8 text.

    Args:
        repo_path: Absolute or relative path to the repository root.
        file_path: Path to the target file, relative to ``repo_path``.
            Example: ``"src/app/main.py"``.
        max_chars: Optional maximum number of characters to return. When set,
            content beyond the limit is truncated and marked.

    Behavior:
    - Rejects path traversal outside ``repo_path`` and raises ``ValueError``.
    - Raises ``FileNotFoundError`` when the file does not exist.
    - Reads text with ``encoding="utf-8"`` and ``errors="ignore"``.
    - When ``max_chars`` is provided, content is truncated to at most that many
      characters with a ``...[TRUNCATED]...`` marker appended.

    Returns:
        The file content as a string, possibly truncated when ``max_chars`` is set.
    """
    repo = resolve_repo(repo_path)
    full_path = (repo / file_path).resolve()

    try:
        full_path.relative_to(repo)
    except ValueError as exc:
        raise ValueError(
            f"file_path must stay inside repo_path: {file_path}"
        ) from exc

    if not full_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    if max_chars is not None and len(content) > max_chars:
        return content[:max_chars] + "\n\n...[TRUNCATED]..."

    return content
