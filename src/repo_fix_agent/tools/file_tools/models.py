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


class CreateFileResult(BaseModel):
    """Structured result returned by ``create_file``."""

    path: str = Field(description="Relative file path that was written")
    created: bool = Field(description="Whether a new file was created")
    overwritten: bool = Field(description="Whether an existing file was replaced")
    parent_created: bool = Field(
        description="Whether missing parent directories were created"
    )


class ReplaceInFileResult(BaseModel):
    """Structured result returned by ``replace_in_file``."""

    path: str = Field(description="Relative file path that was updated")
    replacements: int = Field(description="Number of replacements applied")


class ApplyPatchResult(BaseModel):
    """Structured result returned by ``apply_patch``."""

    path: str = Field(description="Relative file path that was updated")
    hunks_applied: int = Field(description="Number of patch hunks applied")
