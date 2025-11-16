"""Defines the learning agent that produces learning roadmaps and resources."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from tools.base import Tool
from tools.learning_tools import LearningTools


@dataclass
class RoadmapRequest:
    direction: str
    current_level: str
    target_level: str


class LearningAgent:
    """Generates study paths, resources, and job search tips for a direction."""

    _LEVEL_ORDER = ["новичок", "стажер", "выпускник", "junior", "middle", "senior"]

    _BASE_STEPS: Dict[str, List[str]] = {
        "frontend": [
            "HTML5/доступность и семантическая разметка",
            "Современный CSS: flex/grid, responsive дизайн, препроцессоры",
            "JavaScript/TypeScript и принципы асинхронности",
            "Фреймворки (React/Vue/Svelte) и state-менеджмент",
            "Тестирование (Jest/Vitest, e2e Cypress/Playwright) и CI",
        ],
        "backend": [
            "Языки (Python/Go/Java) + чистый код",
            "Базы данных SQL/NoSQL, транзакции и моделирование",
            "REST/gRPC, аутентификация, документация API",
            "Архитектура (слои, очереди, кэш), контейнеризация",
            "Наблюдаемость, метрики, профилирование и безопасность",
        ],
        "data": [
            "Статистика, вероятность, основы линейной алгебры",
            "Python / R, библиотеки анализа данных",
            "ETL, SQL, визуализация, BI-инструменты",
            "Машинное обучение, валидация, MLOps базовые практики",
            "Коммуникация результатов, сторителлинг и продуктовый контекст",
        ],
    }

    _LEARNING_RESOURCES: Dict[str, List[str]] = {
        "frontend": [
            "freecodecamp.org дорожки по HTML/CSS/JS",
            "Frontend Masters / Udemy React путь",
            "Книги: 'You Don't Know JS', 'Refactoring UI'",
            "Сообщества: Frontend Conf, VK FE-сообщество",
        ],
        "backend": [
            "Книги: 'Clean Architecture', 'Designing Data-Intensive Applications'",
            "Практика: exercism.org, codewars, pet-проекты",
            "Курсы: Stepik backend на Python/Go, Coursera",
            "Сообщества: backend hangouts, подкаст Radio-T",
        ],
        "data": [
            "Курс Andrew Ng ML, Stepik 'Аналитик данных'",
            "Книги: 'Storytelling with Data', 'Python for Data Analysis'",
            "Песочницы Kaggle, Yandex Praktikum тренажёры",
            "Telegram чаты data-сообщества, митапы ODS.ai",
        ],
    }

    _JOB_STEPS = [
        "Подготовка портфолио и описание проектов с цифрами",
        "Оптимизация резюме под ключевые слова и требования",
        "Тренировка интервью (тех и soft-skills) и тестовые задания",
        "Системная подача откликов и ведение CRM откликов",
        "Нетворкинг: митапы, профильные чаты, open-source вклад",
    ]

    _JOB_RESOURCES = [
        "hh.ru, habr career, linkedin.com/jobs",
        "t.me/junior_jobs, карьерные каналы направления",
        "Github для open-source активности",
        "Job trackers (Airtable, Notion) для контроля откликов",
    ]

    def __init__(self) -> None:
        self._toolset = LearningTools()

    def tools(self) -> List[Tool]:
        return self._toolset.tools()

    def build_roadmap(self, request: RoadmapRequest) -> Dict[str, object]:
        direction = request.direction.lower().strip()
        normalized_direction = self._normalize_direction(direction)
        steps = self._BASE_STEPS.get(normalized_direction, [
            "Базовая теория выбранного направления",
            "Инструменты и стек, принятый в индустрии",
            "Практика через пет-проекты и open-source",
            "Тестирование, документация и совместная работа",
            "Продвинутая специализация и решение прикладных задач",
        ])
        resources = self._LEARNING_RESOURCES.get(normalized_direction, [
            "Coursera/Stepik курсы по направлению",
            "Книги и официальные гайды от ведущих компаний",
            "Практические площадки (Kaggle, GitHub Issues)",
            "Профильные подкасты, конференции, митапы",
        ])

        time_estimate = self._estimate_time(request.current_level, request.target_level)
        learning_steps = self._tailor_learning_steps(steps, request.current_level)

        return {
            "user_input": {
                "направление": request.direction,
                "стартовый уровень": request.current_level,
                "желаемый уровень": request.target_level,
            },
            "примерная длительность": time_estimate,
            "шаги обучения": learning_steps,
            "рекомендуемые ресурсы обучения": resources,
            "шаги по устройству": self._JOB_STEPS,
            "ресурсы для поиска работы": self._JOB_RESOURCES,
            "поддержка": "Ты на правильном пути — бери план по шагам и пиши, если нужна помощь. Удачи!",
        }

    def _normalize_direction(self, direction: str) -> str:
        if any(key in direction for key in ("front", "ui", "web")):
            return "frontend"
        if any(key in direction for key in ("back", "server", "api")):
            return "backend"
        if any(key in direction for key in ("data", "аналит", "ml", "ds")):
            return "data"
        return "generic"

    def _estimate_time(self, current: str, target: str) -> str:
        try:
            start_index = self._LEVEL_ORDER.index(current.lower())
        except ValueError:
            start_index = 0
        try:
            target_index = self._LEVEL_ORDER.index(target.lower())
        except ValueError:
            target_index = start_index + 1

        delta = max(0, target_index - start_index)
        months = 2 + delta * 3
        return f"{months}–{months + 2} месяцев при занятиях 12–15 часов в неделю"

    def _tailor_learning_steps(self, steps: List[str], current_level: str) -> List[str]:
        level = current_level.lower()
        if level in ("выпускник", "стажер"):
            return steps
        if level in ("junior", "middle"):
            return [step for step in steps if "Тестирование" not in step][:4] + ["Усиление soft-skills и product-мышления"]
        return ["Фундаментальные основы + синтаксис"] + steps[:3] + [
            "Мини-проект каждую неделю с ретро и анализом"
        ]
