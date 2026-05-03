from __future__ import annotations

import pytest

from repo_fix_agent.graph.state import create_initial_state
from repo_fix_agent.nodes import run_tests as rt
from repo_fix_agent.schemas.run_tests import RunTestsOutput
from repo_fix_agent.tools.command_tools.models import CommandResult


def test_run_tests_skips_when_needs_tests_false() -> None:
    state = create_initial_state(
        user_request="Explain the auth flow",
        repo_path="/tmp/repo",
        test_command="",
    )
    state["needs_tests"] = False

    update = rt.run_tests_node(state)

    assert update == {
        "tests_passed": True,
        "test_output": "Skipped tests because needs_tests was false.",
    }


def test_run_tests_uses_existing_command(monkeypatch: pytest.MonkeyPatch) -> None:
    state = create_initial_state(
        user_request="Fix login test",
        repo_path="/tmp/repo",
        test_command="pytest",
    )

    def fake_run_test_command(repo_path: str, command: str, timeout: int = 120) -> CommandResult:
        assert repo_path == "/tmp/repo"
        assert command == "pytest"
        return CommandResult(
            command=["pytest"],
            cwd=repo_path,
            stdout="2 passed\n",
            stderr="",
            returncode=0,
            success=True,
        )

    monkeypatch.setattr(rt, "run_test_command", fake_run_test_command)

    update = rt.run_tests_node(state)

    assert update["tests_passed"] is True
    assert update["test_command"] == "pytest"
    assert "Command: pytest" in update["test_output"]
    assert "2 passed" in update["test_output"]


def test_run_tests_asks_llm_for_command_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    state = create_initial_state(
        user_request="Fix login test",
        repo_path="/tmp/repo",
        test_command="",
    )
    state["request_summary"] = "Fix login test"
    state["project_type"] = "python"
    state["test_strategy"] = "Run pytest after the edit."
    state["changed_files"] = ["src/auth.py"]
    state["test_files"] = ["tests/test_auth.py"]

    captured: dict[str, object] = {}

    class FakeStructured:
        def invoke(self, messages: object) -> RunTestsOutput:
            captured["messages"] = messages
            return RunTestsOutput(
                command="pytest",
                skipped=False,
                summary="Use pytest because this repo looks like a Python project.",
            )

    class FakeChat:
        def with_structured_output(self, schema: object) -> FakeStructured:
            return FakeStructured()

    class FakeGemini:
        @property
        def chat(self) -> FakeChat:
            return FakeChat()

    def fake_run_test_command(repo_path: str, command: str, timeout: int = 120) -> CommandResult:
        return CommandResult(
            command=["pytest"],
            cwd=repo_path,
            stdout="ok\n",
            stderr="",
            returncode=0,
            success=True,
        )

    monkeypatch.setattr(rt, "GeminiChatModel", lambda **_: FakeGemini())
    monkeypatch.setattr(rt, "run_test_command", fake_run_test_command)

    update = rt.run_tests_node(state)

    assert update["tests_passed"] is True
    assert update["test_command"] == "pytest"
    assert "Use pytest because this repo looks like a Python project." in update["test_output"]

    messages = captured["messages"]
    assert isinstance(messages, list)
    assert "tests/test_auth.py" in messages[1].content


def test_run_tests_returns_failure_when_no_safe_command(monkeypatch: pytest.MonkeyPatch) -> None:
    state = create_initial_state(
        user_request="Fix login test",
        repo_path="/tmp/repo",
        test_command="",
    )

    class FakeStructured:
        def invoke(self, messages: object) -> RunTestsOutput:
            return RunTestsOutput(
                command="",
                skipped=False,
                summary="No safe test command could be determined.",
            )

    class FakeChat:
        def with_structured_output(self, schema: object) -> FakeStructured:
            return FakeStructured()

    class FakeGemini:
        @property
        def chat(self) -> FakeChat:
            return FakeChat()

    monkeypatch.setattr(rt, "GeminiChatModel", lambda **_: FakeGemini())

    update = rt.run_tests_node(state)

    assert update["tests_passed"] is False
    assert update["test_output"] == "No safe test command could be determined."
    assert update["errors"] == ["No safe test command could be determined."]


def test_run_tests_rejects_disallowed_llm_recommendation(monkeypatch: pytest.MonkeyPatch) -> None:
    state = create_initial_state(
        user_request="Verify a Next.js change",
        repo_path="/tmp/repo",
        test_command="",
    )
    state["project_type"] = "nextjs"

    class FakeStructured:
        def invoke(self, messages: object) -> RunTestsOutput:
            return RunTestsOutput(
                command="npm run dev",
                skipped=False,
                summary=(
                    "No explicit test command or test files were found. For a Next.js "
                    "project, running npm run dev is the safest way to verify changes."
                ),
            )

    class FakeChat:
        def with_structured_output(self, schema: object) -> FakeStructured:
            return FakeStructured()

    class FakeGemini:
        @property
        def chat(self) -> FakeChat:
            return FakeChat()

    monkeypatch.setattr(rt, "GeminiChatModel", lambda **_: FakeGemini())

    update = rt.run_tests_node(state)

    assert update["tests_passed"] is False
    assert "Model recommended disallowed command: npm run dev" in update["test_output"]
    assert update["errors"] == ["Disallowed recommended test command: npm run dev"]
