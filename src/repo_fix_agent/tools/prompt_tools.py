"""Load packaged markdown prompts from ``repo_fix_agent.prompts``."""

from pathlib import Path


def load_prompt(name: str) -> str:
    path = Path(__file__).resolve().parents[1] / "prompts" / f"{name}.md"
    return path.read_text(encoding="utf-8")
