from pathlib import Path

from langchain_core.tools import tool

EXCLUDED_DIRS = {"node_modules", ".git", "dist", "build", ".venv"}


@tool
def list_files(repo_path: str) -> list[str]:
    """
    List all readable file paths under a repository root.

    Use this to discover candidate files before calling ``read_file``.

    Args:
        repo_path: Absolute or relative path to the repository root directory.

    Returns:
        A sorted list of file paths relative to ``repo_path`` using POSIX style
        separators (``/``), for example ``src/repo_fix_agent/main.py``.

    Notes:
    - Skips common noise directories:
      ``node_modules``, ``.git``, ``dist``, ``build``, ``.venv``.
    - Raises ``ValueError`` if ``repo_path`` does not exist or is not a directory.
    """
    root = Path(repo_path).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"repo_path does not exist: {repo_path}")
    if not root.is_dir():
        raise ValueError(f"repo_path is not a directory: {repo_path}")

    files: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        files.append(path.relative_to(root).as_posix())
    files.sort()
    return files


@tool
def read_file(repo_path: str, file_path: str) -> str:
    """
    Read a single text file inside ``repo_path`` and return its full contents.

    Use this when the agent already knows which file to inspect.

    Args:
        repo_path: Absolute or relative path to the repository root.
        file_path: Path to the target file, relative to ``repo_path``.
            Example: ``"src/app/main.py"``.

    Safety behavior:
    - Rejects path traversal outside ``repo_path``.
    - Rejects paths that include ignored directories
      (``node_modules``, ``.git``, ``dist``, ``build``, ``.venv``).
    - Raises clear ``ValueError`` messages for invalid inputs.
    """
    root = Path(repo_path).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"repo_path does not exist: {repo_path}")
    if not root.is_dir():
        raise ValueError(f"repo_path is not a directory: {repo_path}")

    candidate = (root / file_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"file_path must stay inside repo_path: {file_path}"
        ) from exc

    rel_parts = candidate.relative_to(root).parts
    if any(part in EXCLUDED_DIRS for part in rel_parts):
        raise ValueError(f"file_path is inside an excluded directory: {file_path}")

    if not candidate.exists():
        raise ValueError(f"file_path does not exist: {file_path}")
    if not candidate.is_file():
        raise ValueError(f"file_path is not a file: {file_path}")

    return candidate.read_text(encoding="utf-8")