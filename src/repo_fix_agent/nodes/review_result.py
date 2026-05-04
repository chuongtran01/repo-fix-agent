from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.llm.model import GeminiChatModel
from repo_fix_agent.schemas.review_result import ReviewResultOutput
from repo_fix_agent.utils.load_prompt import load_prompt

SYSTEM_PROMPT = load_prompt("review_result_system").strip()
USER_PROMPT = load_prompt("review_result_user").strip()


def review_result_node(state: AgentState) -> dict[str, object]:
    """Review the latest verification result and choose the next workflow action."""
    print("Reviewing result...")

    user_request = state["user_request"]
    request_summary = state["request_summary"] or user_request

    model_name = os.getenv("PRIMARY_MODEL", "gemini-2.5-flash")
    llm = GeminiChatModel(model=model_name)
    structured = llm.chat.with_structured_output(ReviewResultOutput)

    user_prompt = USER_PROMPT.format(
        user_request=user_request,
        request_summary=request_summary,
        plan=state.get("plan", []),
        target_files=state.get("target_files", []),
        changed_files=state.get("changed_files", []),
        iteration=state["iteration"],
        max_iterations=state["max_iterations"],
        tests_passed=state.get("tests_passed", False),
        test_command=state.get("test_command", ""),
        test_output=state.get("test_output", ""),
        errors=state.get("errors", []),
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]
    response: ReviewResultOutput = structured.invoke(messages)
    review_notes = list(response.review_notes)
    iteration = state["iteration"]
    max_iterations = state["max_iterations"]

    update: dict[str, object] = {
        "review_category": response.category,
        "review_outcome": response.outcome,
        "review_reason": response.reason,
        "review_notes": review_notes,
    }

    if response.outcome == "retry":
        next_iteration = iteration + 1
        if next_iteration >= max_iterations:
            update["review_outcome"] = "failure"
            update["review_reason"] = (
                f"{response.reason} Retry limit reached after "
                f"{max_iterations} iteration(s)."
            ).strip()
            update["review_notes"] = review_notes + [
                "Stopped retrying because max_iterations was reached."
            ]
        else:
            update["iteration"] = next_iteration

    return update
