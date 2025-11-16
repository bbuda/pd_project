"""Learning related tool implementations."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .base import Tool
from .pdf_utils import extract_text_from_pdf, summarize_chunks

CAREER_PATHS = [
    {
        "role": "Frontend разработчик",
        "road": ["HTML/CSS", "React/TypeScript", "Тестирование", "Участие в open-source"],
    },
    {
        "role": "Data аналитик",
        "road": ["SQL и статистика", "BI инструменты", "A/B тесты", "Продуктовая аналитика"],
    },
]

LEARNING_MATERIALS = [
    {"title": "Stepik курсы", "effectiveness": "90% при прохождении проектов"},
    {"title": "MIT OpenCourseWare", "effectiveness": "80% благодаря глубине теории"},
    {"title": "YouTube спринты", "effectiveness": "65%: подходит для повторения"},
]

CONCEPT_EXPLANATIONS = {
    "docker": "Представь контейнер как коробку с приложением и всем, что ему нужно.",
    "api": "API — контракт: ты отправляешь запрос, сервис отвечает строго по договорённости.",
    "ml": "ML-модель — это функция, которая учится на данных, чтобы предсказывать ответы.",
}


@dataclass
class LearningTools:
    max_pdf_chars: int = 2000
    _tools: List[Tool] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._tools = [self._career_paths(), self._learning_materials(), self._concept_explanations()]

    def tools(self) -> List[Tool]:
        return list(self._tools)

    def _career_paths(self) -> Tool:
        def handler(payload: Dict[str, object]) -> Dict[str, object]:
            return {"paths": CAREER_PATHS}

        return Tool(
            name="learning_career_paths",
            description="Возвращает карьерные пути и образовательные траектории",
            input_schema={"type": "object", "properties": {}},
            handler=handler,
        )

    def _learning_materials(self) -> Tool:
        def handler(payload: Dict[str, object]) -> Dict[str, object]:
            pdf_excerpt = None
            pdf_path = payload.get("pdf_path")
            if pdf_path:
                pdf_excerpt = summarize_chunks([extract_text_from_pdf(Path(str(pdf_path)))], max_chars=self.max_pdf_chars)
            return {"materials": LEARNING_MATERIALS, "pdf_excerpt": pdf_excerpt}

        return Tool(
            name="learning_materials_with_reviews",
            description="Обучающие материалы и оценка их эффективности. Может разбирать PDF конспекты.",
            input_schema={
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "description": "Файл с материалами"},
                },
            },
            handler=handler,
        )

    def _concept_explanations(self) -> Tool:
        def handler(payload: Dict[str, object]) -> Dict[str, object]:
            term = (payload.get("term") or "").lower()
            if term and term in CONCEPT_EXPLANATIONS:
                return {"concepts": {term: CONCEPT_EXPLANATIONS[term]}}
            return {"concepts": CONCEPT_EXPLANATIONS}

        return Tool(
            name="learning_simple_explanations",
            description="Дает простые объяснения сложных концепций",
            input_schema={
                "type": "object",
                "properties": {
                    "term": {"type": "string", "description": "Конкретный термин"},
                },
            },
            handler=handler,
        )
