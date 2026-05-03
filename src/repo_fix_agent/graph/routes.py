from __future__ import annotations

from typing import Literal

from repo_fix_agent.graph.state import AgentState

ReviewRoute = Literal["inspect_repo", "rollback", "final_summary"]


def route_after_review(state: AgentState) -> ReviewRoute:
    """Choose the next graph node from the latest review outcome."""
    outcome = state.get("review_outcome", "failure")

    if outcome == "retry":
        return "inspect_repo"
    if outcome == "rollback":
        return "rollback"
    return "final_summary"
