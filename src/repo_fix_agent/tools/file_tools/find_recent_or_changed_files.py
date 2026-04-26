from langchain_core.tools import tool


@tool
def find_recent_or_changed_files(repo_path: str, max_results: int = 10) -> list[str]:
    pass
