from langchain_core.tools import tool

from ._helpers import resolve_repo
from .constants import MAX_FILE_SIZE


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
