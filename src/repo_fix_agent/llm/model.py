"""Reusable Gemini chat model built on LangChain's ``ChatGoogleGenerativeAI``."""

from __future__ import annotations

import os
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI


class GeminiChatModel:
    """
    Thin wrapper around ``ChatGoogleGenerativeAI`` for consistent setup across nodes.

    Reads ``GOOGLE_API_KEY`` or ``GEMINI_API_KEY`` from the environment when
    ``api_key`` is not passed explicitly. Raises ``ValueError`` when no API key
    is available so callers fail fast with a clear configuration error.
    """

    def __init__(
        self,
        *,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.0,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        resolved_key = (
            api_key
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        )
        if not resolved_key:
            raise ValueError(
                "Missing Gemini API key. Set GOOGLE_API_KEY or GEMINI_API_KEY."
            )
        init_kwargs: dict[str, Any] = {
            "model": model,
            "temperature": temperature,
        }
        init_kwargs["api_key"] = resolved_key
        init_kwargs.update(kwargs)

        self._chat = ChatGoogleGenerativeAI(**init_kwargs)

    @property
    def chat(self) -> ChatGoogleGenerativeAI:
        """The underlying LangChain runnable (invoke / ainvoke / bind_tools, etc.)."""
        return self._chat

    def bind(self, **kwargs: Any) -> ChatGoogleGenerativeAI:
        """Return a new runnable with extra runtime config (e.g. tools, tags)."""
        return self._chat.bind(**kwargs)
