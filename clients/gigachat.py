"""Minimal client for the GigaChat API with offline fallback."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


DEFAULT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


class GigaChatError(RuntimeError):
    """Raised when the API request fails."""


@dataclass
class GigaChatClient:
    """Tiny wrapper that sends chat-completion requests to GigaChat."""

    api_key: Optional[str] = None
    base_url: str = DEFAULT_API_URL
    model: str = "GigaChat"
    timeout: int = 30

    def __post_init__(self) -> None:
        if not self.api_key:
            self.api_key = os.getenv("GIGACHAT_API_KEY")
        if env_url := os.getenv("GIGACHAT_API_URL"):
            self.base_url = env_url

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, tool_choice: str | None = "auto") -> Dict[str, Any]:
        if not self.available:
            return self._offline_answer(messages)

        payload: Dict[str, Any] = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.post(self.base_url, headers=headers, json=payload, timeout=self.timeout)
        if not response.ok:
            raise GigaChatError(f"GigaChat API error: {response.status_code} {response.text}")
        return response.json()

    def _offline_answer(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Returns a deterministic assistant message when API is unavailable."""

        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), {"content": ""})
        summary = last_user.get("content", "")
        content = (
            "(GigaChat offline) Я сохранил контекст сообщения и могу использовать локальные инструменты."
            f" Запрос: {summary[:400]}"
        )
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": content,
                    }
                }
            ]
        }
