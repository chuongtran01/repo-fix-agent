"""Shared LangGraph agent state (see ARCHITECTURE.md — Core Agent State)."""

from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict):
    """State carried through the repo-fix workflow graph."""

    user_request: str
    repo_path: str

    relevant_files: list[str]
    files_read: dict[str, str]

    plan: list[str]
    changed_files: list[str]
    original_files: dict[str, str]

    test_command: str
    test_output: str
    tests_passed: bool

    iteration: int
    max_iterations: int

    errors: list[str]
    final_summary: str


def create_initial_state(
    *,
    user_request: str,
    repo_path: str,
    test_command: str,
    max_iterations: int = 2,
) -> AgentState:
    """Build a full initial state for ``graph.invoke`` / ``graph.astream``."""
    state: AgentState = {
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
