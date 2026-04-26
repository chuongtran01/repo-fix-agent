from langchain_core.tools import tool
import re
from .list_files import list_files


@tool
def find_test_files(repo_path: str, max_results: int = 100) -> list[str]:
    """
    Find likely test files by filename convention across common ecosystems.

    Args:
        repo_path: Absolute or relative path to the repository root.
        max_results: Maximum number of matching file paths to return.

    Returns:
        A list of relative file paths that match known test naming patterns.

    Patterns currently recognized include:
    - JavaScript/TypeScript: ``*.test.(ts|tsx|js|jsx)``, ``*.spec.(ts|tsx|js|jsx)``
    - Python: ``test_*.py``, ``*_test.py``
    - Java: ``*Test.java``, ``*Tests.java``

    Notes:
    - Candidate files come from ``list_files(repo_path)``.
    - Matching is case-insensitive.
    - Path separators are normalized to ``/`` before regex matching.
    - Returns early when ``max_results`` is reached.
    """

    test_patterns = [
        re.compile(r".*\.test\.(ts|tsx|js|jsx)$", re.IGNORECASE),
        re.compile(r".*\.spec\.(ts|tsx|js|jsx)$", re.IGNORECASE),
        re.compile(r"(^|.*/)test_.*\.py$", re.IGNORECASE),
        re.compile(r".*_test\.py$", re.IGNORECASE),
        re.compile(r".*Test\.java$", re.IGNORECASE),
        re.compile(r".*Tests\.java$", re.IGNORECASE),
    ]

    results: list[str] = []

    for file_path in list_files(repo_path):
        normalized = file_path.replace("\\", "/")

        if any(pattern.match(normalized) for pattern in test_patterns):
            results.append(file_path)

        if len(results) >= max_results:
            return results

    return results
