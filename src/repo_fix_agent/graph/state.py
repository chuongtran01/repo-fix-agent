"""Shared LangGraph agent state (see ARCHITECTURE.md — Core Agent State)."""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class AgentState(TypedDict):
    """State carried through the repo-fix workflow graph."""

    user_request: str
    repo_path: str

    task_type: NotRequired[
        Literal["bug_fix", "test_fix", "refactor",
                "feature", "explanation", "unknown"]
    ]
    request_summary: NotRequired[str]
    likely_areas: NotRequired[list[str]]
    needs_tests: NotRequired[bool]
    risk_level: NotRequired[Literal["low", "medium", "high"]]
    constraints: NotRequired[list[str]]

    relevant_files: NotRequired[list[str]]
    files_read: NotRequired[dict[str, str]]

    plan: NotRequired[list[str]]
    changed_files: NotRequired[list[str]]
    original_files: NotRequired[dict[str, str]]

    test_command: NotRequired[str]
    test_output: NotRequired[str]
    tests_passed: NotRequired[bool]

    iteration: int
    max_iterations: int

    errors: NotRequired[list[str]]
    final_summary: NotRequired[str]


def create_initial_state(
    *,
    user_request: str,
    repo_path: str,
    test_command: str,
    max_iterations: int = 2,
) -> AgentState:
    """Build a full initial state for ``graph.invoke`` / ``graph.astream``."""
    state: AgentState = {
        "task_type": "unknown",
        "request_summary": "",
        "likely_areas": [],
        "needs_tests": True,
        "risk_level": "medium",
        "constraints": [],
        "user_request": user_request,
        "repo_path": repo_path,
        "relevant_files": [],
        "files_read": {},
        "plan": [],
        "changed_files": [],
        "original_files": {},
        "test_command": test_command,
        "test_output": "",
        "tests_passed": False,
        "iteration": 0,
        "max_iterations": max_iterations,
        "errors": [],
        "final_summary": "",
    }
    return state
