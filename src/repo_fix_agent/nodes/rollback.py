from __future__ import annotations

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.tools.file_tools._helpers import resolve_repo_file_path


def rollback_node(state: AgentState) -> dict[str, object]:
    """Restore original file contents for edited files when review requests rollback."""
    print("Rolling back changes...")

    repo_path = state["repo_path"]
    original_files = state.get("original_files", {})
    changed_files = state.get("changed_files", [])
    existing_notes = list(state.get("review_notes", []))
    restored_files: list[str] = []
    removed_files: list[str] = []
    rolled_back_files = sorted(set(state.get("rolled_back_files", [])) | set(changed_files))

    for file_path in changed_files:
        _, full_path = resolve_repo_file_path(repo_path, file_path)

        if file_path in original_files:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(original_files[file_path], encoding="utf-8")
            restored_files.append(file_path)
            continue

        if full_path.exists():
            full_path.unlink()
            removed_files.append(file_path)

    notes = existing_notes + [
        f"Rollback restored {len(restored_files)} file(s) and removed {len(removed_files)} newly created file(s)."
    ]
    if restored_files:
        notes.append("Restored files: " + ", ".join(restored_files))
    if removed_files:
        notes.append("Removed files: " + ", ".join(removed_files))

    return {
        "changed_files": changed_files,
        "rolled_back_files": rolled_back_files,
        "review_notes": notes,
    }
