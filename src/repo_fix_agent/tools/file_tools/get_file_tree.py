from pathlib import Path
from langchain_core.tools import tool
from ._helpers import resolve_repo
from .constants import IGNORE_DIRS, IGNORE_EXTENSIONS


@tool
def get_file_tree(repo_path: str, max_depth: int = 3, max_entries: int = 300) -> str:
    """
    Build a compact, human-readable tree view of the repository.

    Args:
        repo_path: Absolute or relative path to the repository root.
        max_depth: Maximum directory depth to traverse (root is depth 0).
        max_entries: Maximum number of tree entries (files + dirs) to include
            before truncating output.

    Returns:
        A newline-delimited tree string, starting with ``<repo_name>/``.

    Notes:
    - Ignores directories in ``IGNORE_DIRS`` and files with extensions in
      ``IGNORE_EXTENSIONS``.
    - Entries are sorted with directories first, then files (case-insensitive).
    - If ``max_entries`` is reached, ``...[TRUNCATED]...`` is appended.
    """

    repo = resolve_repo(repo_path)
    lines: list[str] = [str(repo.name) + "/"]
    count = 0

    def walk_dir(directory: Path, prefix: str = "", depth: int = 0) -> None:
        nonlocal count

        if depth >= max_depth or count >= max_entries:
            return

        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except PermissionError:
            return

        entries = [
            e for e in entries
            if e.name not in IGNORE_DIRS
            and e.suffix.lower() not in IGNORE_EXTENSIONS
        ]

        for index, entry in enumerate(entries):
            if count >= max_entries:
                lines.append(prefix + "...[TRUNCATED]...")
                return

            connector = "└── " if index == len(entries) - 1 else "├── "
            lines.append(prefix + connector + entry.name)
            count += 1

            if entry.is_dir():
                extension = "    " if index == len(entries) - 1 else "│   "
                walk_dir(entry, prefix + extension, depth + 1)

    walk_dir(repo)

    return "\n".join(lines)
