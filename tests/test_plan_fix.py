from __future__ import annotations

import pytest

from repo_fix_agent.graph.state import create_initial_state
from repo_fix_agent.nodes import plan_fix as pf
from repo_fix_agent.schemas.plan_fix import PlanFixOutput


def test_plan_fix_node_maps_structured_output(monkeypatch: pytest.MonkeyPatch) -> None:
    state = create_initial_state(
        user_request="Fix the failing login test",
        repo_path="/tmp/repo",
        test_command="pytest",
    )
    state["request_summary"] = "Fix failing login test"
    state["task_type"] = "bug_fix"
    state["needs_tests"] = True
    state["risk_level"] = "low"
    state["constraints"] = ["Keep changes minimal"]
    state["project_type"] = "python"
    state["repo_summary"] = "Small auth service"
    state["relevant_files"] = ["src/auth.py", "tests/test_auth.py"]
    state["file_reasons"] = {"src/auth.py": "login logic", "tests/test_auth.py": "failing test"}
    state["files_read"] = {"src/auth.py": "def login():\n    pass\n"}
    state["file_summaries"] = {"tests/test_auth.py": {"summary": "auth tests"}}
    state["test_files"] = ["tests/test_auth.py"]
    state["inspection_notes"] = ["Login path appears to be under auth.py"]

    captured: dict[str, object] = {}

    class FakeStructured:
        def invoke(self, messages: object) -> PlanFixOutput:
            captured["messages"] = messages
            return PlanFixOutput(
                plan=[
                    "Inspect login handling in src/auth.py against expectations in tests/test_auth.py",
                    "Update the login logic with the smallest safe change to satisfy the failing test",
                    "Run the targeted auth tests first, then rerun pytest if needed",
                ],
                target_files=["src/auth.py", "tests/test_auth.py"],
                risks=["Changing auth logic may affect other login paths."],
                test_strategy="Run tests/test_auth.py first, then pytest if the fix touches shared auth code.",
            )

    class FakeChat:
        def with_structured_output(self, schema: object) -> FakeStructured:
            return FakeStructured()

    class FakeGemini:
        @property
        def chat(self) -> FakeChat:
            return FakeChat()

    monkeypatch.setattr(pf, "GeminiChatModel", lambda **_: FakeGemini())

    update = pf.plan_fix_node(state)

    assert update == {
        "plan": [
            "Inspect login handling in src/auth.py against expectations in tests/test_auth.py",
            "Update the login logic with the smallest safe change to satisfy the failing test",
            "Run the targeted auth tests first, then rerun pytest if needed",
        ],
        "target_files": ["src/auth.py", "tests/test_auth.py"],
        "plan_risks": ["Changing auth logic may affect other login paths."],
        "test_strategy": "Run tests/test_auth.py first, then pytest if the fix touches shared auth code.",
    }

    messages = captured["messages"]
    assert isinstance(messages, list)
    assert "src/auth.py" in messages[1].content
    assert "Keep changes minimal" in messages[1].content
