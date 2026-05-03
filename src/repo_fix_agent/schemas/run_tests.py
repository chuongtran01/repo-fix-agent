from __future__ import annotations

from pydantic import BaseModel, Field


class RunTestsOutput(BaseModel):
    """Structured output returned by the ``run_tests`` node."""

    command: str = Field(
        default="",
        description=(
            "The verification command that should be run. Empty when "
            "no safe command could be determined."
        ),
    )
    skipped: bool = Field(
        default=False,
        description=(
            "Whether verification was intentionally skipped, for example because "
            "`needs_tests` was false."
        ),
    )
    summary: str = Field(
        default="",
        description=(
            "Short explanation of the recommendation, such as why a command was chosen, "
            "why verification was skipped, or why no safe command was available."
        ),
    )
