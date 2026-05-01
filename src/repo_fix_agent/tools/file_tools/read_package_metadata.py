from ._helpers import resolve_repo
from .models import PackageMetadataResult
from .read_file import read_file
def read_package_metadata(repo_path: str) -> dict[str, str]:
    """
    Read common package and project metadata files from the repo root.

    Args:
        repo_path: Absolute or relative path to the repository root.

    Returns:
        A dictionary mapping metadata file path -> file content for files that
        exist and are readable. Missing or unreadable files are skipped.

    Notes:
    - Candidate files include ecosystem markers such as ``package.json``,
      ``pyproject.toml``, ``requirements.txt``, ``Pipfile``, ``pom.xml``,
      ``build.gradle*``, ``README*``, and common frontend config files.
    - File reads use ``read_file(...)``, so the same truncation and path-safety
      behavior applies here.
    """
    metadata_files = [
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "Pipfile",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "README.md",
        "README.txt",
        "tsconfig.json",
        "vite.config.ts",
        "vite.config.js",
        "next.config.ts",
        "next.config.js",
        "next.config.mjs",
    ]

    repo = resolve_repo(repo_path)
    result: dict[str, str] = {}

    for file_path in metadata_files:
        try:
            full_path = repo / file_path
            if full_path.exists() and full_path.is_file():
                result[file_path] = read_file(repo_path, file_path)
        except Exception:
            continue

    return PackageMetadataResult(files=result).files
