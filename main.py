"""CLI entry point for the multi-agent career assistant."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from agents.orchestrator import Orchestrator


def _read_text_argument(text: Optional[str], path: Optional[str]) -> str:
    chunks = []
    if text:
        chunks.append(text)
    if path:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Файл {file_path} не найден")
        chunks.append(file_path.read_text(encoding="utf-8"))
    if not chunks:
        raise ValueError("Нужно передать --text или --file")
    return "\n".join(chunks)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Мульти-агентный карьерный помощник")
    subparsers = parser.add_subparsers(dest="command", required=True)

    roadmap = subparsers.add_parser("roadmap", help="Сформировать учебный план")
    roadmap.add_argument("--direction", required=True, help="Направление (frontend и т.д.)")
    roadmap.add_argument("--current", required=True, help="Текущий уровень (например, выпускник)")
    roadmap.add_argument("--target", required=True, help="Желаемый уровень (например, junior)")

    templates = subparsers.add_parser("templates", help="Получить шаблоны резюме/писем")
    templates.add_argument("--group", help="Группа (например, 'ИТ-продукты')")

    analyze_doc = subparsers.add_parser("analyze-doc", help="Анализ резюме или письма")
    analyze_doc.add_argument("--type", required=True, choices=["resume", "cover"], help="Тип документа")
    analyze_doc.add_argument("--text", help="Текст для анализа")
    analyze_doc.add_argument("--file", help="Путь к файлу с текстом")

    vacancy = subparsers.add_parser("analyze-vacancy", help="Анализ вакансии")
    vacancy.add_argument("--text", help="Текст вакансии")
    vacancy.add_argument("--file", help="Файл с описанием вакансии")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    orchestrator = Orchestrator()

    if args.command == "roadmap":
        result = orchestrator.create_roadmap(args.direction, args.current, args.target)
    elif args.command == "templates":
        result = orchestrator.fetch_templates(args.group)
    elif args.command == "analyze-doc":
        text = _read_text_argument(args.text, args.file)
        result = orchestrator.review_document(text, args.type)
    elif args.command == "analyze-vacancy":
        text = _read_text_argument(args.text, args.file)
        result = orchestrator.review_vacancy(text)
    else:
        parser.error("Неизвестная команда")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
