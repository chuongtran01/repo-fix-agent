from __future__ import annotations

from repo_fix_agent.graph.state import create_initial_state
from repo_fix_agent.nodes.final_summary import final_summary_node


def test_final_summary_includes_rolled_back_files() -> None:
    state = create_initial_state(
        user_request="Fix login test",
        repo_path="/tmp/repo",
        test_command="pytest",
    )
    state["request_summary"] = "Fix login test"
    state["review_outcome"] = "rollback"
    state["review_reason"] = "Verification failed after risky edits."
    state["changed_files"] = ["src/auth.py"]
    state["rolled_back_files"] = ["src/auth.py"]

    update = final_summary_node(state)

    assert "Changed files:" in update["final_summary"]
    assert "Rolled back files:" in update["final_summary"]
    assert "- src/auth.py" in update["final_summary"]
