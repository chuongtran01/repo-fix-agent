from __future__ import annotations

from repo_fix_agent.graph.state import AgentState


def final_summary_node(state: AgentState) -> dict[str, object]:
    """Build a concise final summary from the latest workflow state."""
    request_summary = state.get("request_summary") or state["user_request"]
    changed_files = state.get("changed_files", [])
    rolled_back_files = state.get("rolled_back_files", [])
    review_outcome = state.get("review_outcome", "failure")
    review_category = state.get("review_category", "manual_review_required")
    review_reason = state.get("review_reason", "")
    review_notes = state.get("review_notes", [])
    tests_passed = state.get("tests_passed", False)
    test_command = state.get("test_command", "")
    test_output = state.get("test_output", "")
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 0)

    lines = [
        f"Request: {request_summary}",
        f"Workflow outcome: {review_outcome}",
        f"Verification category: {review_category}",
    ]

    if review_reason:
        lines.append(f"Stopped because: {review_reason}")

    if changed_files:
        lines.append("Changed files:")
        lines.extend(f"- {path}" for path in changed_files)
    else:
        lines.append("Changed files: none")

    if rolled_back_files:
        lines.append("Rolled back files:")
        lines.extend(f"- {path}" for path in rolled_back_files)

    if test_command:
        lines.append(f"Verification command: {test_command}")
    else:
        lines.append("Verification command: none")
    lines.append(f"Verification passed: {'yes' if tests_passed else 'no'}")
    lines.append(f"Iterations used: {iteration} of {max_iterations}")

    if review_notes:
        lines.append("Review notes:")
        lines.extend(f"- {note}" for note in review_notes)

    if test_output:
        lines.append("Verification output:")
        lines.append(test_output)

    return {"final_summary": "\n".join(lines).strip()}
