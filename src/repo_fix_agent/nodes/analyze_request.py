"""LangGraph node: classify the user's request (structured LLM output)."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.llm.model import GeminiChatModel
from repo_fix_agent.schemas.analyze_request import AnalyzeRequestOutput
from repo_fix_agent.utils.load_prompt import load_prompt


SYSTEM_PROMPT = load_prompt("analyze_request").strip()

USER_PROMPT = "User request: {user_request}"


def analyze_request_node(state: AgentState) -> dict[str, object]:
    """Analyze the user's request and return a structured partial state update."""
    user_request = state["user_request"]

    llm = GeminiChatModel()
    structured = llm.chat.with_structured_output(AnalyzeRequestOutput)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=USER_PROMPT.format(user_request=user_request)),
    ]
    response: AnalyzeRequestOutput = structured.invoke(messages)

    return {
        "task_type": response.task_type,
        "request_summary": response.summary,
        "likely_areas": response.likely_areas,
        "needs_tests": response.needs_tests,
        "risk_level": response.risk_level,
        "constraints": response.constraints,
    }
