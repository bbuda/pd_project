"""Career oriented tools that can be invoked by the orchestrator."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .base import Tool
from .pdf_utils import extract_text_from_pdf, summarize_chunks


SUCCESSFUL_RESUMES = [
    "Frontend разработчик: 2 пет-проекта, вклад в open-source и рост производительности UI на 30%.",
    "Data engineer: автоматизация пайплайна, снижение стоимости хранения на 18%, стек Airflow + Spark.",
    "Product менеджер: запуск discovery цикла, рост MAU на 22% и NPS +14 пунктов.",
]

FAILED_RESUMES = [
    "Резюме без конкретики, только список обязанностей и без цифр.",
    "Перегруженный документ на 7 страниц, отсутствуют контакты и ссылки.",
    "Копия описания вакансии, нет уникальных достижений кандидата.",
]

VACANCY_DESCRIPTIONS = [
    {
        "title": "Хорошая стажировка frontend",
        "label": "good",
        "reasons": ["есть наставник", "оплачиваемая", "четкие задачи и стек"],
    },
    {
        "title": "Сомнительная роль аналитика",
        "label": "bad",
        "reasons": ["нет договора", "оплата после испытательного срока", "24/7"],
    },
]

INTERVIEW_QA = [
    {
        "question": "Как вы объясните свой провал в проекте?",
        "answer": "Расскажите по схеме STAR, добавьте уроки и то, как исправили процесс.",
    },
    {
        "question": "Чем гордитесь больше всего?",
        "answer": "Опишите конкретный вклад и метрику результата, завершите связью с ролью.",
    },
    {
        "question": "Что сделаете в первые 90 дней?",
        "answer": "Сбор контекста, быстрая победа, фокус на коммуникацию и фидбек.",
    },
]


@dataclass
class CareerTools:
    """Creates Tool definitions with optional PDF ingestion."""

    max_pdf_chars: int = 2000
    _tools: List[Tool] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._tools = [self._resume_examples_tool(), self._vacancy_judger_tool(), self._interview_qa_tool()]

    def tools(self) -> List[Tool]:
        return list(self._tools)

    def _resume_examples_tool(self) -> Tool:
        def handler(payload: Dict[str, object]) -> Dict[str, object]:
            pdf_excerpt = None
            pdf_path = payload.get("pdf_path")
            if pdf_path:
                pdf_excerpt = summarize_chunks([extract_text_from_pdf(Path(str(pdf_path)))], max_chars=self.max_pdf_chars)
            include_failures = payload.get("include_failures", True)
            return {
                "successful": SUCCESSFUL_RESUMES,
                "unsuccessful": FAILED_RESUMES if include_failures else [],
                "pdf_excerpt": pdf_excerpt,
            }

        return Tool(
            name="career_resume_examples",
            description=(
                "Возвращает примеры успешных/неуспешных резюме и по желанию добавляет извлечённый текст"
                " из прикреплённого PDF резюме пользователя."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "description": "Путь до PDF резюме кандидата"},
                    "include_failures": {
                        "type": "boolean",
                        "description": "Добавлять ли неудачные примеры",
                        "default": True,
                    },
                },
            },
            handler=handler,
        )

    def _vacancy_judger_tool(self) -> Tool:
        def handler(payload: Dict[str, object]) -> Dict[str, object]:
            pdf_excerpt = None
            pdf_path = payload.get("pdf_path")
            if pdf_path:
                pdf_excerpt = summarize_chunks([extract_text_from_pdf(Path(str(pdf_path)))], max_chars=self.max_pdf_chars)
            notes = payload.get("notes")
            return {
                "vacancies": VACANCY_DESCRIPTIONS,
                "comment": notes or "",
                "pdf_excerpt": pdf_excerpt,
            }

        return Tool(
            name="career_vacancy_reviews",
            description="Показывает примеры хороших и плохих описаний вакансий, может разобрать PDF вакансии",
            input_schema={
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "description": "Путь к PDF описанию вакансии"},
                    "notes": {
                        "type": "string",
                        "description": "Дополнительные пользовательские комментарии",
                    },
                },
            },
            handler=handler,
        )

    def _interview_qa_tool(self) -> Tool:
        def handler(payload: Dict[str, object]) -> Dict[str, object]:
            topic = (payload.get("topic") or "").lower()
            results = INTERVIEW_QA
            if topic:
                results = [item for item in INTERVIEW_QA if topic in item["question"].lower()]
                if not results:
                    results = INTERVIEW_QA
            return {"qa": results}

        return Tool(
            name="career_interview_qa",
            description="Предоставляет реальные вопросы и ответы с собеседований",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Фильтр по ключевому слову"},
                },
            },
            handler=handler,
        )
