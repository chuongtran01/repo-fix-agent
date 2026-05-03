from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ReviewResultOutput(BaseModel):
    """Structured output returned by the ``review_result`` node."""

    outcome: Literal["success", "retry", "failure", "rollback"] = Field(
        description=(
            "The next action after reviewing test results: finish successfully, "
            "retry the fix loop, stop with failure, or rollback changes."
        )
    )
    reason: str = Field(
        description=(
            "Short explanation of why this outcome was chosen, including the key "
            "signal from test output or execution failure."
        )
    )
    review_notes: list[str] = Field(
        default_factory=list,
        description=(
            "Additional notes for the next node, such as retry guidance, setup "
            "issues, or dependency-related concerns."
        ),
    )
