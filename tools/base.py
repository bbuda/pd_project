"""Definitions for describing callable tools exposed to the LLM orchestrator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class Tool:
    """Simple container describing a callable tool."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: ToolHandler

    def run(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.handler(payload or {})


class ToolRegistry:
    """Keeps track of the tools exposed to the orchestrator."""

    def __init__(self, tools: Iterable[Tool]):
        self._tools: Dict[str, Tool] = {tool.name: tool for tool in tools}

    def describe_for_llm(self) -> List[Dict[str, Any]]:
        descriptions: List[Dict[str, Any]] = []
        for tool in self._tools.values():
            descriptions.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                }
            )
        return descriptions

    def run(self, name: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"Tool {name} is not registered")
        return self._tools[name].run(payload)

    def names(self) -> List[str]:
        return list(self._tools.keys())
