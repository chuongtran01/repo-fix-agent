from __future__ import annotations

from typing import Any

from ._helpers import resolve_repo_file_path
from .models import ApplyPatchResult


def apply_patch(
    repo_path: str,
    file_path: str,
    changes: list[dict[str, Any]],
) -> dict[str, object]:
    """
    Apply multiple targeted replacements to a file atomically.

    Args:
        repo_path: Absolute or relative path to the repository root.
        file_path: Relative path to the file that should be updated.
        changes: Ordered patch hunks. Each hunk must contain ``old`` and ``new``
            keys and may include ``replace_all`` (bool, default ``False``).

    Behavior:
    - Rejects path traversal outside ``repo_path``.
    - Reads the file once, applies all hunks in order, and writes only if every
      hunk succeeds.
    - For a hunk with ``replace_all=False``, the ``old`` text must appear
      exactly once in the current working content.
    - Raises ``ValueError`` for malformed hunks, missing text, or ambiguous
      single-match edits.

    Returns:
        A structured result with the number of patch hunks applied.
    """
    _, full_path = resolve_repo_file_path(repo_path, file_path)
    if not full_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    content = full_path.read_text(encoding="utf-8", errors="ignore")
    updated = content

    for index, change in enumerate(changes, start=1):
        if "old" not in change or "new" not in change:
            raise ValueError(f"patch hunk {index} must include 'old' and 'new'")

        old = change["old"]
        new = change["new"]
        replace_all = bool(change.get("replace_all", False))

        if not isinstance(old, str) or not isinstance(new, str):
            raise ValueError(f"patch hunk {index} 'old' and 'new' must be strings")
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
        hunks_applied=len(changes),
    ).model_dump()
