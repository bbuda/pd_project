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

    chat = subparsers.add_parser("chat", help="Чат с ассистентом (поддерживает PDF)")
    chat.add_argument("--message", help="Сообщение для одноразового ответа")
    chat.add_argument("--pdf", action="append", help="Прикрепить PDF документ к чату")

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
    elif args.command == "chat":
        if args.pdf:
            for pdf in args.pdf:
                path = Path(pdf)
                if not path.exists():
                    raise FileNotFoundError(f"Файл {pdf} не найден")
                doc = orchestrator.attach_pdf(path)
                print(f"Прикреплён {doc.name}")
        if args.message:
            result = orchestrator.chat(args.message)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        print("Запущен чат. Используй /attach <путь к pdf> для добавления документов и 'exit' для выхода.")
        while True:
            try:
                user_input = input("Вы: ").strip()
            except EOFError:
                print()
                break
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit", "выход"}:
                break
            if user_input.startswith("/attach"):
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    print("Укажи путь к файлу после /attach")
                    continue
                path = Path(parts[1])
                if not path.exists():
                    print(f"Файл {path} не найден")
                    continue
                doc = orchestrator.attach_pdf(path)
                print(f"Добавлен {doc.name}")
                continue
            reply = orchestrator.chat(user_input)
            print(f"Ассистент: {reply['answer']}")
        return 0
    else:
        parser.error("Неизвестная команда")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
