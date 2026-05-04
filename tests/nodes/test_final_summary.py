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
    state["review_category"] = "code_or_test_failure"
    state["review_reason"] = "Verification failed after risky edits."
    state["review_notes"] = ["Rollback restored the last attempted change."]
    state["changed_files"] = ["src/auth.py"]
    state["rolled_back_files"] = ["src/auth.py"]
    state["tests_passed"] = False
    state["test_output"] = "AssertionError: expected 200"

    update = final_summary_node(state)

    summary = update["final_summary"]

    assert "Workflow outcome: rollback" in summary
    assert "Verification category: code_or_test_failure" in summary
    assert "Stopped because: Verification failed after risky edits." in summary
    assert "Changed files:" in summary
    assert "Rolled back files:" in summary
    assert "Verification command: pytest" in summary
    assert "Verification passed: no" in summary
    assert "Iterations used: 0 of 2" in summary
    assert "Review notes:" in summary
    assert "Verification output:" in summary
    assert "- src/auth.py" in summary
