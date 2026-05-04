from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ReviewResultOutput(BaseModel):
    """Structured output returned by the ``review_result`` node."""

    category: Literal[
        "verification_passed",
        "code_or_test_failure",
        "command_selection_failure",
        "setup_or_dependency_failure",
        "timeout_or_infra_failure",
        "manual_review_required",
    ] = Field(
        description=(
            "The main kind of verification result observed: a real code/test "
            "failure, a bad verification command choice, a setup or dependency "
            "problem, a timeout or infrastructure issue, a clean pass, or a "
            "fallback manual-review case."
        )
    )
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
