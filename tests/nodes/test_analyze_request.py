from __future__ import annotations

import pytest

from repo_fix_agent.graph.state import create_initial_state
from repo_fix_agent.nodes import analyze_request as ar
from repo_fix_agent.schemas.analyze_request import AnalyzeRequestOutput


def test_analyze_request_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    class FakeStructured:
        def invoke(self, messages: object) -> AnalyzeRequestOutput:
            return AnalyzeRequestOutput(
                task_type="bug_fix",
                summary="Fix login",
                likely_areas=["auth", "tests"],
                needs_tests=True,
                risk_level="low",
                constraints=["Keep changes minimal"],
            )

    class FakeChat:
        def with_structured_output(self, schema: object) -> FakeStructured:
            return FakeStructured()

    class FakeGemini:
        @property
        def chat(self) -> FakeChat:
            return FakeChat()

    monkeypatch.setattr(ar, "GeminiChatModel", lambda **_: FakeGemini())

    state = create_initial_state(
        user_request="Fix the failing login test",
        repo_path="/tmp/repo",
        test_command="pytest",
    )
    update = ar.analyze_request_node(state)

    assert update == {
        "task_type": "bug_fix",
        "request_summary": "Fix login",
        "likely_areas": ["auth", "tests"],
        "needs_tests": True,
        "risk_level": "low",
        "constraints": ["Keep changes minimal"],
    }


def test_analyze_request_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    state = create_initial_state(
        user_request="Fix the failing login test",
        repo_path="/tmp/repo",
        test_command="pytest",
    )
    with pytest.raises(
        ValueError,
        match="Missing Gemini API key. Set GOOGLE_API_KEY or GEMINI_API_KEY.",
    ):
        ar.analyze_request_node(state)


def test_analyze_request_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    def _boom(**_: object) -> object:
        raise RuntimeError("boom")

    monkeypatch.setattr(ar, "GeminiChatModel", _boom)

    state = create_initial_state(
        user_request="hello",
        repo_path="/tmp/repo",
        test_command="pytest",
    )
    with pytest.raises(RuntimeError, match="boom"):
        ar.analyze_request_node(state)
