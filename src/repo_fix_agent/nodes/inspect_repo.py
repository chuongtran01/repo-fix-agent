import os
from collections.abc import Callable

from langchain_core.tools import tool

from repo_fix_agent.graph.state import AgentState
from repo_fix_agent.llm.model import GeminiChatModel
from repo_fix_agent.tools.file_tools.constants import TOOL_READ_CHAR_LIMIT
from repo_fix_agent.tools.file_tools import (
    detect_project_type as detect_project_type_impl,
    find_test_files as find_test_files_impl,
    get_file_tree as get_file_tree_impl,
    grep_code as grep_code_impl,
    list_files as list_files_impl,
    read_file as read_file_impl,
    read_package_metadata as read_package_metadata_impl,
    search_code as search_code_impl,
)
from repo_fix_agent.tools.git_tools import (
    find_recent_or_changed_files as find_recent_or_changed_files_impl,
)
from repo_fix_agent.schemas.inspect_repo import InspectRepoOutput
from repo_fix_agent.tools.summary_tools.summarize_file import summarize_file
from repo_fix_agent.utils.load_prompt import load_prompt

SYSTEM_PROMPT = load_prompt("inspect_repo_system").strip()
USER_PROMPT = load_prompt("inspect_repo_user").strip()

MAX_FILES_TO_KEEP = 8
STATE_RAW_CONTENT_CHAR_LIMIT = 12_000


def get_create_agent() -> Callable[..., object]:
    """Import the LangChain agent factory lazily for easier testing and compatibility."""
    from langchain.agents import create_agent

    return create_agent


def build_inspect_tools(repo_path: str) -> list[object]:
    """Build repo-scoped tools so the model never has to supply ``repo_path``."""

    @tool
    def detect_project_type() -> dict[str, object]:
        """
        Detect the likely project/runtime type from root config files.

        Use this early when you need high-level repo context.
        Returns a small structured summary with a primary type, detected types,
        and the marker files that triggered the result.
        """
        return detect_project_type_impl(repo_path)

    @tool
    def find_test_files(max_results: int = 100) -> list[str]:
        """
        Find likely test files by common naming conventions.

        Use this when the request sounds test-related or you want candidate
        verification files. Returns relative file paths only.
        """
        return find_test_files_impl(repo_path, max_results=max_results)

    @tool
    def get_file_tree(max_depth: int = 3, max_entries: int = 300) -> str:
        """
        Show the repository structure as a compact tree.

        Use this for broad directory discovery. Prefer `search_code` or
        `grep_code` when you already have a concrete term to look for.
        """
        return get_file_tree_impl(
            repo_path,
            max_depth=max_depth,
            max_entries=max_entries,
        )

    @tool
    def grep_code(pattern: str, max_results: int = 50) -> list[dict[str, object]]:
        """
        Search text files with a regex and return matching lines.

        Use this when you need exact line-level evidence, not just likely file
        paths. Returns file path, line number, and matched line text.
        """
        return grep_code_impl(repo_path, pattern, max_results=max_results)

    @tool
    def list_files() -> list[str]:
        """
        List candidate files in the repository.

        Use this for broad file discovery when you do not yet know where to
        look. Returns relative file paths only.
        """
        return list_files_impl(repo_path)

    @tool
    def read_file(file_path: str) -> str:
        """
        Read one file from the repository by relative path.

        Use this after you already know which file to inspect. Large files are
        truncated to keep tool output bounded.
        """
        return read_file_impl(repo_path, file_path, max_chars=TOOL_READ_CHAR_LIMIT)

    @tool
    def read_package_metadata() -> dict[str, str]:
        """
        Read common root-level metadata and config files.

        Use this for quick project context such as package managers, build
        config, or framework setup. Returns a mapping of file path to content.
        """
        return read_package_metadata_impl(repo_path)

    @tool
    def search_code(query: str, max_results: int = 20) -> list[str]:
        """
        Find likely relevant files from a keyword or symbol.

        Use this when you have a concrete search term and want ranked file
        paths. Prefer `grep_code` when you need matching lines.
        """
        return search_code_impl(repo_path, query, max_results=max_results)

    @tool
    def find_recent_or_changed_files(
        recent_limit: int = 20,
        changed_limit: int = 50,
    ) -> dict[str, object]:
        """
        Inspect recent and currently changed Git files.

        Use this when the request may be related to recent breakage or current
        work in progress. Returns changed-file buckets plus recent files.
        """
        return find_recent_or_changed_files_impl(
            repo_path,
            recent_limit=recent_limit,
            changed_limit=changed_limit,
        )

    return [
        detect_project_type,
        find_test_files,
        get_file_tree,
        grep_code,
        list_files,
        read_file,
        read_package_metadata,
        search_code,
        find_recent_or_changed_files,
    ]


def inspect_repo_node(state: AgentState) -> AgentState:
    """
    Run the inspect-repo LangGraph agent against the repository.

    Builds a tool-enabled model (file and git helpers only) with
    ``InspectRepoOutput`` as the response format, then invokes it with the
    user's request, request summary, ``likely_areas``, and ``needs_tests`` from
    state. The structured response picks candidate paths and notes; this node
    then reads up to ``MAX_FILES_TO_KEEP`` of those paths, keeping raw text
    when under ``STATE_RAW_CONTENT_CHAR_LIMIT`` characters and otherwise calling the
    internal ``summarize_file`` helper (not an LLM-facing tool).

    Returns a partial state update with:
    ``repo_summary``, ``relevant_files``, ``files_read``, ``file_summaries``,
    ``file_reasons``, ``inspection_notes``, ``project_type``, ``test_files``.
    Read failures are appended to ``inspection_notes``.
    """

    print("Inspecting repository...")

    repo_path = state["repo_path"]
    user_request = state["user_request"]

    likely_areas = state.get("likely_areas") or []
    needs_tests = state["needs_tests"] if "needs_tests" in state else True
    request_summary = state["request_summary"] or user_request

    tools = build_inspect_tools(repo_path)

    # Pass a runnable (Gemini API key chat), not a bare model ID string —
    # ``init_chat_model("gemini-...")`` can resolve to Vertex AI and require GCP ADC.
    model_name = os.getenv("PRIMARY_MODEL", "gemini-2.5-flash")
    llm = GeminiChatModel(model=model_name)

    create_agent = get_create_agent()
    agent = create_agent(
        model=llm.chat,
        tools=tools,
        response_format=InspectRepoOutput,
    )

    user_prompt = USER_PROMPT.format(
        repo_path=repo_path,
        user_request=user_request,
        request_summary=request_summary,
        likely_areas=likely_areas,
        needs_tests=needs_tests,
    )

    result = agent.invoke({"messages": [
        ("system", SYSTEM_PROMPT),
        ("user", user_prompt)
    ]})

    structured_result: InspectRepoOutput = result.get("structured_response")

    selected_files = [item.path for item in structured_result.selected_files]
    selected_files = selected_files[:MAX_FILES_TO_KEEP]

    files_read: dict[str, str] = {}
    file_summaries: dict[str, dict] = {}
    inspection_notes = list(structured_result.inspection_notes)

    for file_path in selected_files:
        try:
            content = read_file_impl(repo_path, file_path)

            if len(content) <= STATE_RAW_CONTENT_CHAR_LIMIT:
                files_read[file_path] = content
            else:
                summary = summarize_file(file_path, content)
                file_summaries[file_path] = summary.model_dump()

        except Exception as e:
            inspection_notes.append(f"Failed to read {file_path}: {e}")

    file_reasons = {
        item.path: item.reason
        for item in structured_result.selected_files
    }

    return {
        "repo_summary": structured_result.project_summary,
        "relevant_files": selected_files,
        "files_read": files_read,
        "file_summaries": file_summaries,
        "file_reasons": file_reasons,
        "inspection_notes": inspection_notes,
        "project_type": structured_result.project_type,
        "test_files": structured_result.test_files,
    }
