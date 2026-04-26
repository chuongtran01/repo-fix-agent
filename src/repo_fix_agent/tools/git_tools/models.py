from pydantic import BaseModel, Field


class FindRecentOrChangedFilesResult(BaseModel):
    """Structured result returned by ``find_recent_or_changed_files``."""

    is_git_repo: bool = Field(
        description="Whether repo_path is a Git working tree",
    )
    changed_files: list[str] = Field(
        default_factory=list,
        description="Deduplicated union of staged, unstaged, and untracked paths",
    )
    staged_files: list[str] = Field(
        default_factory=list,
        description="Paths from git diff --cached --name-only",
    )
    unstaged_files: list[str] = Field(
        default_factory=list,
        description="Paths from git diff --name-only",
    )
    untracked_files: list[str] = Field(
        default_factory=list,
        description="Paths from git ls-files --others --exclude-standard",
    )
    recent_files: list[str] = Field(
        default_factory=list,
        description="Unique file paths from recent commit history (git log)",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Non-empty command or validation errors (e.g. not a git repo)",
    )
