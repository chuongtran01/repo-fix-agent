from ._helpers import resolve_repo
from .constants import MAX_FILE_SIZE

def read_file(repo_path: str, file_path: str) -> str:
    """
    Read one file inside ``repo_path`` as UTF-8 text.

    Args:
        repo_path: Absolute or relative path to the repository root.
        file_path: Path to the target file, relative to ``repo_path``.
            Example: ``"src/app/main.py"``.

    Behavior:
    - Rejects path traversal outside ``repo_path`` and raises ``ValueError``.
    - Raises ``FileNotFoundError`` when the file does not exist.
    - Reads text with ``encoding="utf-8"`` and ``errors="ignore"``.
    - Large files are truncated to ``MAX_FILE_SIZE`` characters with a
      ``...[TRUNCATED]...`` marker appended.

    Returns:
        The file content as a string, possibly truncated for very large files.
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

    size = full_path.stat().st_size
    if size > MAX_FILE_SIZE:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(MAX_FILE_SIZE)
        return content + "\n\n...[TRUNCATED]..."

    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
