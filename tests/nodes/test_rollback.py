from __future__ import annotations

from repo_fix_agent.graph.state import create_initial_state
from repo_fix_agent.nodes.rollback import rollback_node


def test_rollback_preserves_audit_trail_and_restores_file(tmp_path) -> None:
    repo_path = tmp_path
    file_path = repo_path / "src" / "auth.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("new content\n", encoding="utf-8")

    state = create_initial_state(
        user_request="Fix login test",
        repo_path=str(repo_path),
        test_command="pytest",
    )
    state["changed_files"] = ["src/auth.py"]
    state["original_files"] = {"src/auth.py": "old content\n"}

    update = rollback_node(state)

    assert file_path.read_text(encoding="utf-8") == "old content\n"
    assert update["changed_files"] == ["src/auth.py"]
    assert update["rolled_back_files"] == ["src/auth.py"]
    assert "Rollback restored 1 file(s) and removed 0 newly created file(s)." in update["review_notes"]
