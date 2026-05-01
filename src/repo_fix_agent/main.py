from pathlib import Path

from dotenv import load_dotenv

from repo_fix_agent.graph.builder import build_graph
from repo_fix_agent.graph.state import create_initial_state

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_REPO_PATH = _REPO_ROOT / "examples" / "demo-app"

load_dotenv()


if __name__ == "__main__":
    app = build_graph().compile()

    user_request = input("Enter your request: ")

    result = app.invoke(
        create_initial_state(
            user_request=user_request,
            repo_path=str(_DEFAULT_REPO_PATH),
            test_command="",
        )
    )

    print(result)
