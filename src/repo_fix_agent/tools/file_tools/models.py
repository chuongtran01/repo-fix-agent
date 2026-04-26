from pydantic import BaseModel, Field


class GrepCodeMatch(BaseModel):
    """One regex match result returned by ``grep_code``."""

    file: str = Field(description="Relative file path")
    line: int = Field(description="1-based line number")
    match: str = Field(description="Matched line text")


class ProjectTypeDetection(BaseModel):
    """Structured result returned by ``detect_project_type``."""

    primary: str = Field(description='Primary detected type, or "unknown"')
    types: list[str] = Field(default_factory=list, description="Detected type labels")
    signals: list[str] = Field(
        default_factory=list,
        description="Files/configs that triggered type detection",
    )


class PackageMetadataResult(BaseModel):
    """Structured result returned by ``read_package_metadata``."""

    files: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of metadata file path to file content",
    )
