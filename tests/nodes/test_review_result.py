from __future__ import annotations

import pytest

from repo_fix_agent.graph.state import create_initial_state
from repo_fix_agent.nodes import review_result as rr
from repo_fix_agent.schemas.review_result import ReviewResultOutput


def test_review_result_node_increments_iteration_on_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = create_initial_state(
        user_request="Fix failing login test",
        repo_path="/tmp/repo",
        test_command="pytest",
    )
    state["request_summary"] = "Fix failing login test"
    state["plan"] = ["Update auth logic", "Run pytest"]
    state["target_files"] = ["src/auth.py"]
    state["changed_files"] = ["src/auth.py"]
    state["tests_passed"] = False
    state["test_output"] = "AssertionError: expected 200"
    state["iteration"] = 0
    state["max_iterations"] = 2

    captured: dict[str, object] = {}

    class FakeStructured:
        def invoke(self, messages: object) -> ReviewResultOutput:
            captured["messages"] = messages
            return ReviewResultOutput(
                category="code_or_test_failure",
                outcome="retry",
                reason="Tests failed with a likely fixable assertion mismatch.",
                review_notes=["Retry the fix with closer attention to auth response handling."],
            )

    class FakeChat:
        def with_structured_output(self, schema: object) -> FakeStructured:
            return FakeStructured()

    class FakeGemini:
        @property
        def chat(self) -> FakeChat:
            return FakeChat()

    monkeypatch.setattr(rr, "GeminiChatModel", lambda **_: FakeGemini())

    update = rr.review_result_node(state)

    assert update == {
        "review_category": "code_or_test_failure",
        "review_outcome": "retry",
        "review_reason": "Tests failed with a likely fixable assertion mismatch.",
        "review_notes": ["Retry the fix with closer attention to auth response handling."],
        "iteration": 1,
    }

    messages = captured["messages"]
    assert isinstance(messages, list)
    assert "AssertionError" in messages[1].content


def test_review_result_node_preserves_iteration_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = create_initial_state(
        user_request="Fix failing login test",
        repo_path="/tmp/repo",
        test_command="pytest",
    )
    state["tests_passed"] = True

    class FakeStructured:
        def invoke(self, messages: object) -> ReviewResultOutput:
            return ReviewResultOutput(
                category="verification_passed",
                outcome="success",
                reason="Verification passed successfully.",
                review_notes=[],
            )

    class FakeChat:
        def with_structured_output(self, schema: object) -> FakeStructured:
            return FakeStructured()

    class FakeGemini:
        @property
        def chat(self) -> FakeChat:
            return FakeChat()

    monkeypatch.setattr(rr, "GeminiChatModel", lambda **_: FakeGemini())

    update = rr.review_result_node(state)

    assert update == {
        "review_category": "verification_passed",
        "review_outcome": "success",
        "review_reason": "Verification passed successfully.",
        "review_notes": [],
    }


def test_review_result_node_stops_retry_at_max_iterations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = create_initial_state(
        user_request="Fix failing login test",
        repo_path="/tmp/repo",
        test_command="pytest",
        max_iterations=2,
    )
    state["tests_passed"] = False
    state["test_output"] = "AssertionError: expected 200"
    state["iteration"] = 1

    class FakeStructured:
        def invoke(self, messages: object) -> ReviewResultOutput:
            return ReviewResultOutput(
                category="code_or_test_failure",
                outcome="retry",
                reason="Tests still look recoverable with another edit.",
                review_notes=["Try a smaller follow-up change."],
            )

    class FakeChat:
        def with_structured_output(self, schema: object) -> FakeStructured:
            return FakeStructured()

    class FakeGemini:
        @property
        def chat(self) -> FakeChat:
            return FakeChat()

    monkeypatch.setattr(rr, "GeminiChatModel", lambda **_: FakeGemini())

    update = rr.review_result_node(state)

    assert update == {
        "review_category": "code_or_test_failure",
        "review_outcome": "failure",
        "review_reason": (
            "Tests still look recoverable with another edit. "
            "Retry limit reached after 2 iteration(s)."
        ),
        "review_notes": [
            "Try a smaller follow-up change.",
            "Stopped retrying because max_iterations was reached.",
        ],
    }
