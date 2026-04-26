from pydantic import BaseModel, Field


class FileSummary(BaseModel):
    path: str = Field(description="File path")
    purpose: str = Field(description="What this file is responsible for")
    key_symbols: list[str] = Field(
        default_factory=list,
        description="Important functions, classes, components, constants, or exports",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Important imports or dependencies used by this file",
    )
    relevant_details: list[str] = Field(
        default_factory=list,
        description="Details that may matter for debugging or editing",
    )
    risk_notes: list[str] = Field(
        default_factory=list,
        description="Anything risky about editing this file",
    )
