"""Shared LangGraph agent state (see ARCHITECTURE.md — Core Agent State)."""

from __future__ import annotations

from typing import Annotated, Literal, NotRequired, TypedDict


class AgentState(TypedDict):
    """State carried through the repo-fix workflow graph."""

    user_request: Annotated[str, "Original user goal or bug description"]
    repo_path: Annotated[str, "Repository root path the agent may read and edit"]

    task_type: NotRequired[
        Annotated[
            Literal[
                "bug_fix",
                "test_fix",
                "refactor",
                "feature",
                "explanation",
                "unknown",
            ],
            "Classified task from analyze_request",
        ]
    ]
    request_summary: NotRequired[
        Annotated[str, "Short restatement of the user request"]
    ]
    likely_areas: NotRequired[
        Annotated[list[str], "Modules, filenames, or keywords to focus inspection"]
    ]
    needs_tests: NotRequired[
        Annotated[bool, "Whether tests or verification should run after changes"]
    ]
    risk_level: NotRequired[
        Annotated[
            Literal["low", "medium", "high"],
            "Estimated risk of making edits for this task",
        ]
    ]
    constraints: NotRequired[
        Annotated[list[str], "Explicit constraints or safety notes from analysis"]
    ]

    repo_summary: NotRequired[
        Annotated[str, "High-level summary of the repo after inspection"]
    ]
    file_summaries: NotRequired[
        Annotated[dict[str, dict], "Per-path structured summaries when content was summarized"]
    ]
    file_reasons: NotRequired[
        Annotated[dict[str, str], "Why each path was selected for follow-up"]
    ]
    inspection_notes: NotRequired[
        Annotated[list[str], "Inspection notes, including tool or read failures"]
    ]
    relevant_files: NotRequired[
        Annotated[list[str], "Paths prioritized for planning or editing"]
    ]
    files_read: NotRequired[
        Annotated[dict[str, str], "Full file text kept when under the raw size limit"]
    ]
    project_type: NotRequired[
        Annotated[str, "Detected project type label (e.g. python, node)"]
    ]
    test_files: NotRequired[
        Annotated[list[str], "Discovered or inferred test file paths"]
    ]

    # Placeholder for the next node to fill in
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
