"""LLM Client — Unified interface for multiple LLM providers."""

from __future__ import annotations

import os
from typing import Any, Optional

from openai import OpenAI


class LLMClient:
    """Unified LLM client supporting OpenAI and Qwen (via OpenRouter)."""

    def __init__(self, provider: Optional[str] = None) -> None:
        self.provider = provider or os.getenv("DEFAULT_MODEL", "openai")

        if self.provider == "qwen":
            self.client = OpenAI(
                api_key=os.getenv("QWEN_API_KEY", ""),
                base_url=os.getenv("QWEN_BASE_URL", "https://openrouter.ai/api/v1"),
            )
            self.model_name = os.getenv("QWEN_MODEL", "qwen/qwen-2.5-72b-instruct")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
            self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def complete(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """Send a completion request to the configured LLM."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def complete_with_system(self, system: str, user: str, **kwargs: Any) -> str:
        """Send a completion with a system message."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=kwargs.get("max_tokens", 1024),
            temperature=kwargs.get("temperature", 0.7),
        )
        return response.choices[0].message.content or ""


_llm_instance: Optional[LLMClient] = None


def get_llm(provider: Optional[str] = None) -> LLMClient:
    """Get or create the singleton LLM client."""
    global _llm_instance
    if _llm_instance is None or (provider and provider != _llm_instance.provider):
        _llm_instance = LLMClient(provider)
    return _llm_instance
