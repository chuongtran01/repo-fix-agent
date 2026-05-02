from __future__ import annotations

from ._helpers import resolve_repo_file_path
from .models import CreateFileResult


def create_file(repo_path: str, file_path: str, content: str) -> dict[str, object]:
    """
    Create or overwrite a file inside ``repo_path``.

    Args:
        repo_path: Absolute or relative path to the repository root.
        file_path: Relative path to the file that should be written.
        content: Full file content to write.

    Behavior:
    - Rejects path traversal outside ``repo_path``.
    - Creates missing parent directories automatically.
    - Overwrites an existing file if present.
    - Raises ``IsADirectoryError`` if the target path is a directory.

    Returns:
        A structured result describing whether the file was created or overwritten.
    """
    _, full_path = resolve_repo_file_path(repo_path, file_path)

    if full_path.exists() and full_path.is_dir():
        raise IsADirectoryError(f"{file_path} is a directory")

    parent = full_path.parent
    parent_created = False
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
        parent_created = True

    existed = full_path.exists()
    full_path.write_text(content, encoding="utf-8")

    return CreateFileResult(
        path=file_path,
        created=not existed,
        overwritten=existed,
        parent_created=parent_created,
    ).model_dump()
