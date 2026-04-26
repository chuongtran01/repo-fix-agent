import os
from pathlib import Path

from .constants import IGNORE_DIRS


def resolve_repo(repo_path: str) -> Path:
    repo = Path(repo_path).resolve()
    if not repo.exists():
        raise ValueError(f"repo_path does not exist: {repo_path}")
    if not repo.is_dir():
        raise ValueError(f"repo_path is not a directory: {repo_path}")
    return repo


def iter_repo_files(repo: Path):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            yield Path(root) / file
