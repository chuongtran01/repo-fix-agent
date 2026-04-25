from dotenv import load_dotenv
from repo_fix_agent.graph.builder import build_graph
from repo_fix_agent.graph.state import create_initial_state

load_dotenv()


if __name__ == "__main__":
    app = build_graph().compile()

    user_request = input("Enter your request: ")

    result = app.invoke(
        create_initial_state(
            user_request=user_request,
            repo_path="",
            test_command="",
        )
    )

    print(result)
