"""High-level orchestrator coordinating career and learning agents."""
from __future__ import annotations

from typing import Dict, List, Optional

from .career_agent import CareerAgent, TemplateResult
from .learning_agent import LearningAgent, RoadmapRequest


class Orchestrator:
    """Routes user intents to the correct specialized agent."""

    def __init__(self) -> None:
        self.learning_agent = LearningAgent()
        self.career_agent = CareerAgent()

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

    def _template_to_dict(self, result: TemplateResult) -> Dict[str, object]:
        return {
            "группа": result.group,
            "примеры резюме": result.resume_examples,
            "примеры сопроводительных": result.cover_examples,
            "шаблоны резюме": result.resume_templates,
            "шаблоны сопроводительных": result.cover_templates,
        }
