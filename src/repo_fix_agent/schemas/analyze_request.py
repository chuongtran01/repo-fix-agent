from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeRequestOutput(BaseModel):
    task_type: Literal[
        "bug_fix",
        "test_fix",
        "refactor",
        "feature",
        "explanation",
        "unknown",
    ] = Field(description="The type of coding task requested.")

    summary: str = Field(description="Short summary of what the user wants.")

    likely_areas: list[str] = Field(
        default_factory=list,
        description="Likely code areas, modules, filenames, or keywords to inspect.",
    )

    needs_tests: bool = Field(
        description="Whether this task should run tests or verification commands."
    )

    risk_level: Literal["low", "medium", "high"] = Field(
        description="Risk level of making changes for this request."
    )

    constraints: list[str] = Field(
        default_factory=list,
        description="Important constraints or safety notes.",
    )
