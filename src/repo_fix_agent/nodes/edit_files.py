from __future__ import annotations

import os
from collections.abc import Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.llm.model import GeminiChatModel
from repo_fix_agent.schemas.edit_files import EditFilesOutput
from repo_fix_agent.tools.file_tools import (
    apply_patch as apply_patch_impl,
    create_file as create_file_impl,
    PatchChange,
    read_file as read_file_impl,
    replace_in_file as replace_in_file_impl,
)
from repo_fix_agent.tools.file_tools._helpers import resolve_repo_file_path
from repo_fix_agent.tools.file_tools.constants import TOOL_READ_CHAR_LIMIT
from repo_fix_agent.utils.load_prompt import load_prompt

SYSTEM_PROMPT = load_prompt("edit_files_system").strip()
USER_PROMPT = load_prompt("edit_files_user").strip()


def get_create_agent() -> Callable[..., object]:
    """Import the LangChain agent factory lazily for easier testing and compatibility."""
    from langchain.agents import create_agent

    return create_agent


def build_edit_tools(
    repo_path: str,
    original_files: dict[str, str],
    actual_changed: set[str],
    internal_notes: list[str],
) -> list[object]:
    """Build repo-scoped edit tools and track actual file changes."""

    def capture_before(file_path: str) -> str | None:
        _, full_path = resolve_repo_file_path(repo_path, file_path)
        if not full_path.exists():
            return None

        previous = full_path.read_text(encoding="utf-8", errors="ignore")
        if file_path not in original_files:
            original_files[file_path] = previous
        return previous

    def record_after(file_path: str, before: str | None) -> None:
        _, full_path = resolve_repo_file_path(repo_path, file_path)
        if not full_path.exists():
            return

        after = full_path.read_text(encoding="utf-8", errors="ignore")
        if before is None or before != after:
            actual_changed.add(file_path)

    @tool
    def read_file(file_path: str) -> str:
        """
        Read one file from the repository by relative path.

        Use this to inspect the latest content before applying an edit. Large
        files are truncated to keep tool output bounded.
        """
        return read_file_impl(repo_path, file_path, max_chars=TOOL_READ_CHAR_LIMIT)

    @tool
    def create_file(file_path: str, content: str) -> dict[str, object]:
        """
        Create or overwrite a file inside the repository.

        Use this when the plan clearly requires a new file or a full-file
        rewrite. Parent directories are created automatically.
        """
        before = capture_before(file_path)
        result = create_file_impl(repo_path, file_path, content)
        record_after(file_path, before)
        if result["created"]:
            internal_notes.append(f"Created {file_path}")
        return result

    @tool
    def replace_in_file(
        file_path: str,
        old: str,
        new: str,
        replace_all: bool = False,
    ) -> dict[str, object]:
        """
        Replace a known snippet inside an existing file.

        Use this for small, exact edits when you know the current text. Prefer
        this over broader patching when the change is local and unambiguous.
        """
        before = capture_before(file_path)
        result = replace_in_file_impl(
            repo_path,
            file_path,
            old,
            new,
            replace_all=replace_all,
        )
        record_after(file_path, before)
        return result

    @tool
    def apply_patch(file_path: str, changes: list[PatchChange]) -> dict[str, object]:
        """
        Apply multiple targeted replacement hunks to an existing file.

        Use this for multi-location edits in the same file. Each hunk should
        specify `old`, `new`, and optional `replace_all`.
        """
        before = capture_before(file_path)
        result = apply_patch_impl(repo_path, file_path, changes)
        record_after(file_path, before)
        return result

    return [read_file, create_file, replace_in_file, apply_patch]


def edit_files_node(state: AgentState) -> dict[str, object]:
    """Apply the planned file edits and track actual filesystem changes."""
    print("Editing files...")

    user_request = state["user_request"]
    request_summary = state["request_summary"] or user_request
    task_type = state["task_type"] if "task_type" in state else "unknown"
    constraints = state.get("constraints", [])
    risk_level = state.get("risk_level", "medium")
    plan = state.get("plan", [])
    target_files = state.get("target_files", [])
    plan_risks = state.get("plan_risks", [])
    test_strategy = state.get("test_strategy", "")
    relevant_files = state.get("relevant_files", [])
    file_reasons = state.get("file_reasons", {})
    files_read = state.get("files_read", {})
    file_summaries = state.get("file_summaries", {})
    test_files = state.get("test_files", [])

    original_files = dict(state.get("original_files", {}))
    actual_changed = set(state.get("changed_files", []))
    internal_notes = list(state.get("edit_notes", []))

    tools = build_edit_tools(
        state["repo_path"],
        original_files,
        actual_changed,
        internal_notes,
    )

    model_name = os.getenv("PRIMARY_MODEL", "gemini-2.5-flash")
    llm = GeminiChatModel(model=model_name)
    create_agent = get_create_agent()
    agent = create_agent(
        model=llm.chat,
        tools=tools,
        response_format=EditFilesOutput,
    )

    user_prompt = USER_PROMPT.format(
        user_request=user_request,
        request_summary=request_summary,
        task_type=task_type,
        constraints=constraints,
        risk_level=risk_level,
        plan=plan,
        target_files=target_files,
        plan_risks=plan_risks,
        test_strategy=test_strategy,
        relevant_files=relevant_files,
        file_reasons=file_reasons,
        files_read=files_read,
        file_summaries=file_summaries,
        test_files=test_files,
    )

    result = agent.invoke(
        {
            "messages": [
                ("system", SYSTEM_PROMPT),
                ("user", user_prompt),
            ]
        }
    )

    structured: EditFilesOutput = result.get("structured_response")
    changed_files = sorted(actual_changed or set(structured.changed_files))
    edit_notes = internal_notes + list(structured.edit_notes)

    return {
        "changed_files": changed_files,
        "original_files": original_files,
        "edit_notes": edit_notes,
    }
