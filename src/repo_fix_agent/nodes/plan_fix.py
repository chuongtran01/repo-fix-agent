from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.llm.model import GeminiChatModel
from repo_fix_agent.schemas.plan_fix import PlanFixOutput
from repo_fix_agent.utils.load_prompt import load_prompt

SYSTEM_PROMPT = load_prompt("plan_fix_system").strip()
USER_PROMPT = load_prompt("plan_fix_user").strip()


def plan_fix_node(state: AgentState) -> dict[str, object]:
    """Plan the smallest safe fix from the inspected repo context."""
    print("Planning fix...")

    user_request = state["user_request"]
    request_summary = state["request_summary"] or user_request
    task_type = state["task_type"] if "task_type" in state else "unknown"
    needs_tests = state["needs_tests"] if "needs_tests" in state else True
    risk_level = state["risk_level"] if "risk_level" in state else "medium"
    constraints = state.get("constraints", [])
    project_type = state.get("project_type", "unknown")
    repo_summary = state.get("repo_summary", "")
    relevant_files = state.get("relevant_files", [])
    file_reasons = state.get("file_reasons", {})
    files_read = state.get("files_read", {})
    file_summaries = state.get("file_summaries", {})
    test_files = state.get("test_files", [])
    inspection_notes = state.get("inspection_notes", [])

    model_name = os.getenv("PRIMARY_MODEL", "gemini-2.5-flash")
    llm = GeminiChatModel(model=model_name)
    structured = llm.chat.with_structured_output(PlanFixOutput)

    user_prompt = USER_PROMPT.format(
        user_request=user_request,
        request_summary=request_summary,
        task_type=task_type,
        needs_tests=needs_tests,
        risk_level=risk_level,
        constraints=constraints,
        project_type=project_type,
        repo_summary=repo_summary,
        relevant_files=relevant_files,
        file_reasons=file_reasons,
        files_read=files_read,
        file_summaries=file_summaries,
        test_files=test_files,
        inspection_notes=inspection_notes,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=user_prompt,
        ),
    ]

    response: PlanFixOutput = structured.invoke(messages)

    return {
        "plan": response.plan,
        "target_files": response.target_files,
        "plan_risks": response.risks,
        "test_strategy": response.test_strategy,
    }
