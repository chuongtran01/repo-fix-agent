from __future__ import annotations

from pathlib import Path

from repo_fix_agent.graph.state import create_initial_state
from repo_fix_agent.nodes import edit_files as ef
from repo_fix_agent.schemas.edit_files import EditFilesOutput


def test_edit_files_node_tracks_originals_and_actual_changes(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    target = tmp_path / "src" / "auth.py"
    target.write_text("def login():\n    pass\n", encoding="utf-8")

    state = create_initial_state(
        user_request="Fix login behavior",
        repo_path=str(tmp_path),
        test_command="pytest",
    )
    state["request_summary"] = "Fix login behavior"
    state["task_type"] = "bug_fix"
    state["constraints"] = ["Keep changes minimal"]
    state["plan"] = ["Update src/auth.py to return True from login."]
    state["target_files"] = ["src/auth.py"]
    state["relevant_files"] = ["src/auth.py"]
    state["files_read"] = {"src/auth.py": "def login():\n    pass\n"}

    class FakeAgent:
        def __init__(self, tools: list[object]) -> None:
            self.tools = {tool.name: tool for tool in tools}

        def invoke(self, payload: dict[str, object]) -> dict[str, object]:
            self.tools["replace_in_file"].func(
                "src/auth.py",
                "pass",
                "return True",
            )
            return {
                "structured_response": EditFilesOutput(
                    changed_files=["src/auth.py"],
                    edit_notes=["Updated login implementation."],
                )
            }

    class FakeGemini:
        @property
        def chat(self) -> object:
            return object()

    monkeypatch.setattr(ef, "GeminiChatModel", lambda **_: FakeGemini())
    monkeypatch.setattr(
        ef,
        "get_create_agent",
        lambda: (lambda **kwargs: FakeAgent(kwargs["tools"])),
    )

    update = ef.edit_files_node(state)

    assert update["changed_files"] == ["src/auth.py"]
    assert update["original_files"] == {"src/auth.py": "def login():\n    pass\n"}
    assert "Updated login implementation." in update["edit_notes"]
    assert target.read_text(encoding="utf-8") == "def login():\n    return True\n"
