from __future__ import annotations

from ._helpers import resolve_repo_file_path
from .models import ApplyPatchResult, PatchChange


def apply_patch(
    repo_path: str,
    file_path: str,
    changes: list[PatchChange | dict[str, object]],
) -> dict[str, object]:
    """
    Apply multiple targeted replacements to a file atomically.

    Args:
        repo_path: Absolute or relative path to the repository root.
        file_path: Relative path to the file that should be updated.
        changes: Ordered patch hunks. Each hunk supplies ``old``, ``new``, and
            optional ``replace_all``. Plain dict inputs are accepted and
            normalized into ``PatchChange``.

    Behavior:
    - Rejects path traversal outside ``repo_path``.
    - Reads the file once, applies all hunks in order, and writes only if every
      hunk succeeds.
    - For a hunk with ``replace_all=False``, the ``old`` text must appear
      exactly once in the current working content.
    - Raises ``ValueError`` for empty ``old`` text, missing text, or ambiguous
      single-match edits.

    Returns:
        A structured result with the number of patch hunks applied.
    """
    _, full_path = resolve_repo_file_path(repo_path, file_path)
    if not full_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    content = full_path.read_text(encoding="utf-8", errors="ignore")
    updated = content

    normalized_changes = [PatchChange.model_validate(change) for change in changes]

    for index, change in enumerate(normalized_changes, start=1):
        old = change.old
        new = change.new
        replace_all = change.replace_all

        if old == "":
            raise ValueError(f"patch hunk {index} 'old' text must not be empty")

        occurrences = updated.count(old)
        if occurrences == 0:
            raise ValueError(f"patch hunk {index} target text not found in {file_path}")
        if not replace_all and occurrences != 1:
            raise ValueError(
                f"patch hunk {index} target text must appear exactly once in {file_path}; "
                f"found {occurrences} matches"
            )

        updated = (
            updated.replace(old, new)
            if replace_all
            else updated.replace(old, new, 1)
        )

    full_path.write_text(updated, encoding="utf-8")

    return ApplyPatchResult(
        path=file_path,
        hunks_applied=len(normalized_changes),
    ).model_dump()
