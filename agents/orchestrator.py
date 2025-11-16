"""High-level orchestrator coordinating career and learning agents."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from clients import GigaChatClient
from tools import Tool, ToolRegistry
from tools.pdf_utils import extract_text_from_pdf, summarize_chunks

from .career_agent import CareerAgent, TemplateResult
from .learning_agent import LearningAgent, RoadmapRequest


@dataclass
class AttachedDocument:
    name: str
    excerpt: str


class Orchestrator:
    """Routes user intents to the correct specialized agent and powers chat."""

    _BASE_PROMPT = (
        "Ты мульти-агентный карьерный ассистент. Используй инструменты карьерного и учебного "
        "агентов, если это помогает ответить. Говори на русском и объясняй рекомендации подробно."
    )

    def __init__(self, llm_client: Optional[GigaChatClient] = None) -> None:
        self.learning_agent = LearningAgent()
        self.career_agent = CareerAgent()
        self._llm_client = llm_client or GigaChatClient()
        self._tool_registry = ToolRegistry(self._collect_tools())
        self._chat_history: List[Dict[str, str]] = []
        self._attachments: List[AttachedDocument] = []

    # ----------------------------------------------------------------------------
    # Classic orchestrator commands
    def create_roadmap(self, direction: str, current_level: str, target_level: str) -> Dict[str, object]:
        request = RoadmapRequest(direction=direction, current_level=current_level, target_level=target_level)
        return self.learning_agent.build_roadmap(request)

    def fetch_templates(self, group: Optional[str] = None) -> List[Dict[str, object]]:
        results = self.career_agent.provide_templates(group)
        return [self._template_to_dict(result) for result in results]

    def review_document(self, text: str, doc_type: str) -> Dict[str, List[str]]:
        return self.career_agent.analyze_document(text, doc_type)

    def review_vacancy(self, text: str) -> Dict[str, object]:
        return self.career_agent.analyze_vacancy(text)

    # ----------------------------------------------------------------------------
    # Chat specific helpers
    def attach_pdf(self, path: Path) -> AttachedDocument:
        text = extract_text_from_pdf(path)
        excerpt = summarize_chunks([text], max_chars=2000)
        document = AttachedDocument(name=path.name, excerpt=excerpt)
        self._attachments.append(document)
        return document

    def chat(self, user_message: str) -> Dict[str, object]:
        user_entry = {"role": "user", "content": user_message}
        system_message = {"role": "system", "content": self._build_system_prompt()}
        messages = [system_message] + self._chat_history + [user_entry]

        if not self._llm_client.available:
            self._chat_history.append(user_entry)
            return self._offline_chat(user_message)

        response = self._llm_client.chat(messages, tools=self._tool_registry.describe_for_llm(), tool_choice="auto")
        assistant_message = response.get("choices", [{}])[0].get("message", {})
        self._chat_history.append(user_entry)
        used_tools: List[Dict[str, object]] = []

        if assistant_message.get("tool_calls"):
            self._chat_history.append({"role": "assistant", "content": assistant_message.get("content", "")})
            used_tools = self._process_tool_calls(assistant_message.get("tool_calls", []))
            follow_up_messages = [{"role": "system", "content": self._build_system_prompt()}] + self._chat_history
            followup_response = self._llm_client.chat(follow_up_messages)
            assistant_content = followup_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            assistant_content = assistant_message.get("content", "")

        self._chat_history.append({"role": "assistant", "content": assistant_content})
        return {
            "answer": assistant_content,
            "used_tools": used_tools,
            "attachments": [doc.name for doc in self._attachments],
        }

    def list_documents(self) -> List[AttachedDocument]:
        return list(self._attachments)

    # ----------------------------------------------------------------------------
    # Internals
    def _process_tool_calls(self, tool_calls: List[Dict[str, object]]) -> List[Dict[str, object]]:
        used_tools: List[Dict[str, object]] = []
        for call in tool_calls:
            function = call.get("function", {})
            name = function.get("name")
            if not name:
                continue
            arguments_raw = function.get("arguments") or "{}"
            try:
                arguments = json.loads(arguments_raw)
            except json.JSONDecodeError:
                arguments = {}
            output = self._tool_registry.run(name, arguments)
            used_tools.append({"name": name, "arguments": arguments, "output": output})
            self._chat_history.append(
                {"role": "tool", "name": name, "content": json.dumps(output, ensure_ascii=False)}
            )
        return used_tools

    def _offline_chat(self, user_message: str) -> Dict[str, object]:
        lower = user_message.lower()
        tool_names: List[str] = []
        if "резюме" in lower:
            tool_names.append("career_resume_examples")
        if "ваканс" in lower:
            tool_names.append("career_vacancy_reviews")
        if any(keyword in lower for keyword in ("обуч", "курс", "материал")):
            tool_names.append("learning_materials_with_reviews")
        if "концеп" in lower or "объясн" in lower:
            tool_names.append("learning_simple_explanations")
        if not tool_names:
            tool_names = ["learning_career_paths"]

        tool_outputs = []
        for name in tool_names:
            try:
                tool_outputs.append({"name": name, "output": self._tool_registry.run(name)})
            except KeyError:
                continue

        summary_parts = ["GigaChat временно недоступен, но я использовал локальные инструменты."]
        for item in tool_outputs:
            summary_parts.append(f"Tool {item['name']}: {json.dumps(item['output'], ensure_ascii=False)[:600]}")
        answer = "\n".join(summary_parts)
        self._chat_history.append({"role": "assistant", "content": answer})
        return {"answer": answer, "used_tools": tool_outputs, "attachments": [doc.name for doc in self._attachments]}

    def _build_system_prompt(self) -> str:
        if not self._attachments:
            return self._BASE_PROMPT
        doc_lines = [f"- {doc.name}: {doc.excerpt[:400]}" for doc in self._attachments]
        return self._BASE_PROMPT + "\n\nПрикрепленные документы:\n" + "\n".join(doc_lines)

    def _collect_tools(self) -> List[Tool]:
        tools: List[Tool] = []
        tools.extend(self.career_agent.tools())
        tools.extend(self.learning_agent.tools())
        return tools

    def _template_to_dict(self, result: TemplateResult) -> Dict[str, object]:
        return {
            "группа": result.group,
            "примеры резюме": result.resume_examples,
            "примеры сопроводительных": result.cover_examples,
            "шаблоны резюме": result.resume_templates,
            "шаблоны сопроводительных": result.cover_templates,
        }
