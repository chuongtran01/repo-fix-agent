from __future__ import annotations

from ._helpers import resolve_repo_file_path
from .models import ReplaceInFileResult


def replace_in_file(
    repo_path: str,
    file_path: str,
    old: str,
    new: str,
    *,
    replace_all: bool = False,
) -> dict[str, object]:
    """
    Replace a known snippet inside a file.

    Args:
        repo_path: Absolute or relative path to the repository root.
        file_path: Relative path to the file that should be updated.
        old: Exact text to replace.
        new: Replacement text.
        replace_all: When ``False``, require exactly one match. When ``True``,
            replace every match.

    Behavior:
    - Rejects path traversal outside ``repo_path``.
    - Raises ``FileNotFoundError`` when the file does not exist.
    - Raises ``ValueError`` if ``old`` is empty.
    - Raises ``ValueError`` if the target text is missing or ambiguous when
      ``replace_all`` is ``False``.

    Returns:
        A structured result with the number of replacements applied.
    """
    if old == "":
        raise ValueError("old text must not be empty")

    _, full_path = resolve_repo_file_path(repo_path, file_path)
    if not full_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    content = full_path.read_text(encoding="utf-8", errors="ignore")
    occurrences = content.count(old)

    if occurrences == 0:
        raise ValueError(f"target text not found in {file_path}")
    if not replace_all and occurrences != 1:
        raise ValueError(
            f"target text must appear exactly once in {file_path}; found {occurrences} matches"
        )

    replacements = occurrences if replace_all else 1
    updated = content.replace(old, new) if replace_all else content.replace(old, new, 1)
    full_path.write_text(updated, encoding="utf-8")

    return ReplaceInFileResult(
        path=file_path,
        replacements=replacements,
    ).model_dump()
