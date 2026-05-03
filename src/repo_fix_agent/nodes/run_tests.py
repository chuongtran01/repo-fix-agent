from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.llm.model import GeminiChatModel
from repo_fix_agent.schemas.run_tests import RunTestsOutput
from repo_fix_agent.tools.command_tools.is_command_allowed import is_command_allowed
from repo_fix_agent.tools.command_tools.run_test_command import run_test_command
from repo_fix_agent.utils.load_prompt import load_prompt

SYSTEM_PROMPT = load_prompt("run_tests_system").strip()
USER_PROMPT = load_prompt("run_tests_user").strip()


def _format_test_result(command: str, *, summary: str, stdout: str, stderr: str, error: str | None) -> str:
    """Build a concise plain-text test execution summary for state."""
    parts = [f"Command: {command}"]
    if summary:
        parts.append(f"Summary: {summary}")
    if stdout:
        parts.append(f"Stdout:\n{stdout}")
    if stderr:
        parts.append(f"Stderr:\n{stderr}")
    if error:
        parts.append(f"Error: {error}")
    return "\n\n".join(parts)


def _recommend_test_command(state: AgentState) -> RunTestsOutput:
    """Ask the model to recommend a safe verification command or skip decision."""
    user_request = state["user_request"]
    request_summary = state["request_summary"] or user_request

    model_name = os.getenv("PRIMARY_MODEL", "gemini-2.5-flash")
    llm = GeminiChatModel(model=model_name)
    structured = llm.chat.with_structured_output(RunTestsOutput)

    user_prompt = USER_PROMPT.format(
        user_request=user_request,
        request_summary=request_summary,
        needs_tests=state.get("needs_tests", True),
        project_type=state.get("project_type", "unknown"),
        test_strategy=state.get("test_strategy", ""),
        test_command=state.get("test_command", ""),
        changed_files=state.get("changed_files", []),
        test_files=state.get("test_files", []),
        inspection_notes=state.get("inspection_notes", []),
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]
    return structured.invoke(messages)


def run_tests_node(state: AgentState) -> dict[str, object]:
    """Choose and run the safest useful verification command for the repo state."""
    print("Running tests...")

    needs_tests = state["needs_tests"] if "needs_tests" in state else True
    existing_errors = list(state.get("errors", []))

    if not needs_tests:
        return {
            "tests_passed": True,
            "test_output": "Skipped tests because needs_tests was false.",
        }

    command = (state.get("test_command") or "").strip()
    recommendation: RunTestsOutput | None = None

    if not command:
        recommendation = _recommend_test_command(state)
        if recommendation.skipped:
            message = recommendation.summary or "Skipped tests based on run_tests recommendation."
            return {
                "tests_passed": True,
                "test_output": message,
            }

        command = recommendation.command.strip()
        if not command:
            message = recommendation.summary or "No safe test command could be determined."
            return {
                "tests_passed": False,
                "test_output": message,
                "errors": existing_errors + [message],
            }
        if not is_command_allowed(command):
            message = (
                recommendation.summary
                or f"Model recommended a disallowed verification command: {command}"
            )
            detailed = (
                f"No safe automated test command could be determined.\n\n"
                f"Model recommended disallowed command: {command}\n\n"
                f"Reason: {message}"
            )
            return {
                "tests_passed": False,
                "test_output": detailed,
                "errors": existing_errors + [f"Disallowed recommended test command: {command}"],
            }

    result = run_test_command(state["repo_path"], command)
    summary = recommendation.summary if recommendation else ""
    output = _format_test_result(
        command,
        summary=summary,
        stdout=result.stdout,
        stderr=result.stderr,
        error=result.error,
    )

    update: dict[str, object] = {
        "test_command": command,
        "tests_passed": result.success,
        "test_output": output,
    }

    if not result.success:
        error_message = result.error or f"Test command failed with exit code {result.returncode}."
        update["errors"] = existing_errors + [error_message]

    return update
