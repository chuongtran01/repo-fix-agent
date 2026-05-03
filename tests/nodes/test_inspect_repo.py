from __future__ import annotations

from pathlib import Path

from repo_fix_agent.graph.state import create_initial_state
from repo_fix_agent.nodes import inspect_repo as ir
from repo_fix_agent.schemas.inspect_repo import InspectRepoOutput, SelectedFile


def test_build_inspect_tools_are_repo_scoped(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("assert True\n", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")

    tools = {tool.name: tool for tool in ir.build_inspect_tools(str(tmp_path))}

    assert "src/app.py" in tools["list_files"].func()
    assert "print('hi')" in tools["read_file"].func("src/app.py")
    assert "src/app.py" in tools["search_code"].func("app")
    assert "tests/test_app.py" in tools["find_test_files"].func()


def test_inspect_repo_node_passes_repo_path_into_prompt(monkeypatch, tmp_path: Path) -> None:
    state = create_initial_state(
        user_request="Inspect the login flow",
        repo_path=str(tmp_path),
        test_command="pytest",
    )
    state["needs_tests"] = False
    state["request_summary"] = "Inspect login flow"
    state["likely_areas"] = ["auth"]

    captured: dict[str, object] = {}

    class FakeAgent:
        def invoke(self, payload: dict[str, object]) -> dict[str, object]:
            captured["payload"] = payload
            return {
                "structured_response": InspectRepoOutput(
                    project_summary="demo",
                    selected_files=[
                        SelectedFile(path="missing.py", reason="candidate"),
                    ],
                    inspection_notes=[],
                    project_type="python",
                    test_files=[],
                )
            }

    class FakeGemini:
        @property
        def chat(self) -> object:
            return object()

    monkeypatch.setattr(ir, "GeminiChatModel", lambda **_: FakeGemini())
    monkeypatch.setattr(ir, "get_create_agent", lambda: (lambda **_: FakeAgent()))

    update = ir.inspect_repo_node(state)

    payload = captured["payload"]
    assert isinstance(payload, dict)
    messages = payload["messages"]
    user_message = messages[1][1]
    assert str(tmp_path) in user_message
    assert "Needs tests:\nFalse" in user_message
    assert update["inspection_notes"]
