from __future__ import annotations

from pydantic import BaseModel, Field


class EditFilesOutput(BaseModel):
    """Structured output returned by the ``edit_files`` node."""

    changed_files: list[str] = Field(
        default_factory=list,
        description=(
            "Relative file paths actually modified by the editing node. Include "
            "only files that were written or created."
        ),
    )
    edit_notes: list[str] = Field(
        default_factory=list,
        description=(
            "Important notes from the edit phase, including notable decisions, "
            "created files, skipped edits, or partial failures."
        ),
    )
