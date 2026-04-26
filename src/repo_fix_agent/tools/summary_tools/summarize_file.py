from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from repo_fix_agent.llm.model import GeminiChatModel
from repo_fix_agent.tools.file_tools.constants import MAX_FILE_SIZE

from .models import FileSummary

SYSTEM_PROMPT = """
You summarize source code files for a repo-aware coding agent.

Return a concise structured summary.

Rules:
- Focus on what the file does.
- Identify important functions/classes/components/exports.
- Mention dependencies/imports that affect behavior.
- Mention details useful for debugging or editing.
- Do not propose changes unless the file clearly indicates a bug.
- Do not include large code snippets.
"""

USER_PROMPT = """
File path: {path}
Was content truncated? {truncated}
File content: ```text{content}```
""".strip()


def summarize_file(
    path: str,
    content: str,
    max_chars: int = MAX_FILE_SIZE,
) -> FileSummary:
    """
    Summarize a source file into compact structured context for graph nodes.

    This is **not** an agent-facing tool: do not register it for the LLM or use
    it as part of the model’s tool-calling / reasoning loop. Call it only from
    trusted internal code (for example ``inspect_repo``) when you need a
    bounded ``FileSummary`` instead of full file text.

    Use when:
    - the file is too long to keep fully in state
    - a node wants compact context before ``plan_fix``
    """

    truncated = False

    if len(content) > max_chars:
        content = content[:max_chars]
        truncated = True

    llm = GeminiChatModel()
    structured = llm.chat.with_structured_output(FileSummary)

    user_content = USER_PROMPT.format(
        path=path, truncated=truncated, content=content)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]
    response: FileSummary = structured.invoke(messages)
    return response
