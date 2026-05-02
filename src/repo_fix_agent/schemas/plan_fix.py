from __future__ import annotations

from pydantic import BaseModel, Field


class PlanFixOutput(BaseModel):
    """Structured planning output returned by the ``plan_fix`` node."""

    plan: list[str] = Field(
        min_length=1,
        description=(
            "Ordered, concrete plan steps for the next node to execute. Steps "
            "should be specific, minimal, and anchored to the inspected files "
            "or summarized areas."
        ),
    )
    target_files: list[str] = Field(
        default_factory=list,
        description=(
            "Relative file paths most likely to be edited. Prefer files already "
            "selected by repo inspection."
        ),
    )
    risks: list[str] = Field(
        default_factory=list,
        description=(
            "Key implementation risks, regressions, or areas that require extra "
            "care while editing."
        ),
    )
    test_strategy: str = Field(
        default="",
        description=(
            "Short description of how to verify the fix, including which tests "
            "to run or update when applicable."
        ),
    )
