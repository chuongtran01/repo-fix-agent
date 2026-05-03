from __future__ import annotations

from repo_fix_agent.graph.state import AgentState


def final_summary_node(state: AgentState) -> dict[str, object]:
    """Build a concise final summary from the latest workflow state."""
    request_summary = state.get("request_summary") or state["user_request"]
    changed_files = state.get("changed_files", [])
    review_outcome = state.get("review_outcome", "failure")
    review_reason = state.get("review_reason", "")
    tests_passed = state.get("tests_passed", False)
    test_command = state.get("test_command", "")
    test_output = state.get("test_output", "")

    lines = [f"Request: {request_summary}", f"Outcome: {review_outcome}"]

    if review_reason:
        lines.append(f"Reason: {review_reason}")

    if changed_files:
        lines.append("Changed files:")
        lines.extend(f"- {path}" for path in changed_files)
    else:
        lines.append("Changed files: none")

    if test_command:
        lines.append(f"Test command: {test_command}")
    lines.append(f"Tests passed: {'yes' if tests_passed else 'no'}")

    if test_output:
        lines.append("Test output:")
        lines.append(test_output)

    return {"final_summary": "\n".join(lines).strip()}
