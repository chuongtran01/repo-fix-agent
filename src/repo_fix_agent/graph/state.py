"""Shared LangGraph agent state (see ARCHITECTURE.md — Core Agent State)."""

from __future__ import annotations

from typing import Annotated, Literal, NotRequired, TypedDict


class AgentState(TypedDict):
    """State carried through the repo-fix workflow graph."""

    user_request: Annotated[str, "Original user goal or bug description"]
    repo_path: Annotated[str,
                         "Repository root path the agent may read and edit"]

    # Analysis phase
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

    # Inspection phase
    repo_summary: NotRequired[
        Annotated[str, "High-level summary of the repo after inspection"]
    ]
    file_summaries: NotRequired[
        Annotated[dict[str, dict],
                  "Per-path structured summaries when content was summarized"]
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
        Annotated[dict[str, str],
                  "Full file text kept when under the raw size limit"]
    ]
    project_type: NotRequired[
        Annotated[str, "Detected project type label (e.g. python, node)"]
    ]
    test_files: NotRequired[
        Annotated[list[str], "Discovered or inferred test file paths"]
    ]

    # Planning phase
    plan: NotRequired[
        Annotated[list[str], "Ordered edit plan produced by the planning node"]
    ]
    target_files: NotRequired[
        Annotated[list[str],
                  "Files the planning node expects the editor to modify"]
    ]
    plan_risks: NotRequired[
        Annotated[list[str],
                  "Implementation or regression risks identified during planning"]
    ]
    test_strategy: NotRequired[
        Annotated[str, "Suggested verification approach produced during planning"]
    ]

    # Editing phase
    changed_files: NotRequired[
        Annotated[list[str], "Files actually modified by the editing node"]
    ]
    original_files: NotRequired[
        Annotated[dict[str, str], "Original content snapshots for files touched by editing"]
    ]
    edit_notes: NotRequired[
        Annotated[list[str], "Notes from the editing node, including tool or edit failures"]
    ]

    # Run tests phase
    test_command: NotRequired[
        Annotated[str, "Verification command requested or selected for the run-tests node"]
    ]
    test_output: NotRequired[
        Annotated[str, "Plain-text output or summary from the verification command"]
    ]
    tests_passed: NotRequired[
        Annotated[bool, "Whether the run-tests phase completed successfully"]
    ]

    # Review result phase
    review_outcome: NotRequired[
        Annotated[
            Literal["success", "retry", "failure", "rollback"],
            "Workflow decision produced after reviewing the latest verification result",
        ]
    ]
    review_category: NotRequired[
        Annotated[
            Literal[
                "verification_passed",
                "code_or_test_failure",
                "command_selection_failure",
                "setup_or_dependency_failure",
                "timeout_or_infra_failure",
                "manual_review_required",
            ],
            "High-level classification of the latest verification result",
        ]
    ]
    review_reason: NotRequired[
        Annotated[str, "Short explanation for the review outcome decision"]
    ]
    review_notes: NotRequired[
        Annotated[list[str], "Additional guidance or follow-up notes from result review"]
    ]

    iteration: Annotated[int, "Current retry-loop attempt count for the workflow"]
    max_iterations: Annotated[int, "Maximum number of retry-loop attempts allowed"]

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
        "target_files": [],
        "plan_risks": [],
        "test_strategy": "",
        "changed_files": [],
        "original_files": {},
        "edit_notes": [],
        "test_command": test_command,
        "test_output": "",
        "tests_passed": False,
        "review_outcome": "failure",
        "review_category": "manual_review_required",
        "review_reason": "",
        "review_notes": [],
        "iteration": 0,
        "max_iterations": max_iterations,
        "errors": [],
        "final_summary": "",
    }
    return state
