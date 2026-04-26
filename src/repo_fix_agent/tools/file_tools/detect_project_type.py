from typing import Any

from langchain_core.tools import tool

from ._helpers import resolve_repo
from .list_files import list_files


@tool
def detect_project_type(repo_path: str) -> dict[str, Any]:
    """
    Detect likely project/runtime types from common root-level marker files.

    Args:
        repo_path: Absolute or relative path to the repository root.

    Returns:
        A dictionary with:
        - ``primary``: first detected type, or ``"unknown"`` if none found
        - ``types``: ordered list of detected types (e.g. ``["node", "typescript"]``)
        - ``signals``: marker files/configs that triggered detection

    Example:
        {
            "primary": "node",
            "types": ["node", "typescript", "nextjs"],
            "signals": ["package.json", "tsconfig.json", "next.config.*"]
        }

    Notes:
        - Detection is heuristic and based on presence checks only.
        - Multiple types can be returned for polyglot or full-stack repos.
    """
    repo = resolve_repo(repo_path)
    files = set(list_files.func(repo_path))

    types: list[str] = []
    signals: list[str] = []

    def has(file_name: str) -> bool:
        return file_name in files or (repo / file_name).exists()

    if has("package.json"):
        types.append("node")
        signals.append("package.json")
    if has("tsconfig.json"):
        types.append("typescript")
        signals.append("tsconfig.json")
    if has("pyproject.toml"):
        types.append("python")
        signals.append("pyproject.toml")
    if has("requirements.txt"):
        if "python" not in types:
            types.append("python")
        signals.append("requirements.txt")
    if has("Pipfile"):
        if "python" not in types:
            types.append("python")
        signals.append("Pipfile")
    if has("pom.xml"):
        types.append("java-maven")
        signals.append("pom.xml")
    if has("build.gradle") or has("build.gradle.kts"):
        types.append("java-gradle")
        signals.append("build.gradle/build.gradle.kts")
    if has("go.mod"):
        types.append("go")
        signals.append("go.mod")
    if has("Cargo.toml"):
        types.append("rust")
        signals.append("Cargo.toml")
    if has("composer.json"):
        types.append("php")
        signals.append("composer.json")
    if has("Gemfile"):
        types.append("ruby")
        signals.append("Gemfile")
    if has("next.config.js") or has("next.config.ts") or has("next.config.mjs"):
        types.append("nextjs")
        signals.append("next.config.*")
    if has("vite.config.ts") or has("vite.config.js"):
        types.append("vite")
        signals.append("vite.config.*")

    primary = types[0] if types else "unknown"
    return {"primary": primary, "types": types, "signals": signals}
