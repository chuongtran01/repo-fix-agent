from ._helpers import resolve_repo
from .list_files import list_files
from .models import ProjectTypeDetection


def detect_project_type(repo_path: str) -> dict[str, object]:
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
        - Detection is heuristic and based on marker-file presence only.
        - Multiple types can be returned for polyglot or full-stack repos.
    """
    repo = resolve_repo(repo_path)
    files = set(list_files(repo_path))

    types: list[str] = []
    signals: list[str] = []

    def add_type(project_type: str, signal: str) -> None:
        if project_type not in types:
            types.append(project_type)
        signals.append(signal)

    def has(file_name: str) -> bool:
        return file_name in files or (repo / file_name).exists()

    if has("package.json"):
        add_type("node", "package.json")
    if has("tsconfig.json"):
        add_type("typescript", "tsconfig.json")
    if has("pyproject.toml"):
        add_type("python", "pyproject.toml")
    if has("requirements.txt"):
        add_type("python", "requirements.txt")
    if has("Pipfile"):
        add_type("python", "Pipfile")
    if has("pom.xml"):
        add_type("java-maven", "pom.xml")
    if has("build.gradle") or has("build.gradle.kts"):
        add_type("java-gradle", "build.gradle/build.gradle.kts")
    if has("go.mod"):
        add_type("go", "go.mod")
    if has("Cargo.toml"):
        add_type("rust", "Cargo.toml")
    if has("composer.json"):
        add_type("php", "composer.json")
    if has("Gemfile"):
        add_type("ruby", "Gemfile")
    if has("next.config.js") or has("next.config.ts") or has("next.config.mjs"):
        add_type("nextjs", "next.config.*")
    if has("vite.config.ts") or has("vite.config.js"):
        add_type("vite", "vite.config.*")

    detection = ProjectTypeDetection(
        primary=types[0] if types else "unknown",
        types=types,
        signals=signals,
    )
    return detection.model_dump()
