"""Career agent responsible for resume templates, analysis, and vacancy checks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TemplateResult:
    group: str
    resume_examples: List[str]
    cover_examples: List[str]
    resume_templates: List[str]
    cover_templates: List[str]


class CareerAgent:
    """Provides resume/cover letter templates and runs document/vacancy reviews."""

    _PROJECT_GROUPS: Dict[str, Dict[str, List[str]]] = {
        "ИТ-продукты": {
            "resume_examples": [
                "Фронтенд-разработчик: стек React/TypeScript, 2 pet-проекта, волонтёрство в open-source.",
                "Python backend: FastAPI, PostgreSQL, описанные кейсы оптимизации API (-30% latency).",
                "Fullstack стажёр: Next.js + Node, учебные проекты с деплоем на Render, участие в хакатонах.",
            ],
            "cover_examples": [
                "Письмо: интерес к продукту, ссылка на демо, 2 абзаца про вклад и мотивацию.",
                "Письмо: акцент на опыт командной разработки и готовность быстро учиться.",
                "Письмо: история проблемы пользователя и как кандидат хочет её решать в компании.",
            ],
            "resume_templates": [
                "ФИО | контакты | GitHub\nЦель\nНавыки (язык, фреймворки)\nОпыт/проекты\nОбразование\nСертификаты",
                "ФИО | роль\nКраткое summary (3 предложения)\nКейсы\nИнструменты\nОбразование и активность",
            ],
            "cover_templates": [
                "Приветствие -> интерес к компании\n1) недавний успех\n2) связь опыта с задачами\nЗакрытие + контакты",
                "Крючок (продукт/миссия)\nОсновные навыки bullets\nПредложение о встрече\nБлагодарность",
            ],
        },
        "Данные и аналитика": {
            "resume_examples": [
                "Аналитик данных: SQL, PowerBI, кейс по снижению затрат на 12%.",
                "Data scientist: sklearn, MLflow, pet-проект рекомендаций, Kaggle bronze.",
                "BI-аналитик: Tableau, автоматизация отчётности, практика A/B тестов.",
            ],
            "cover_examples": [
                "Письмо: метрики, которые кандидат улучшил, и ожидания от роли.",
                "Письмо: акцент на работающие дашборды и взаимодействие с бизнесом.",
                "Письмо: история обучения, почему выбирает именно эту индустрию.",
            ],
            "resume_templates": [
                "ФИО | направление\nSummary с цифрами\nHard skills (SQL, Python, BI)\nПроекты/опыт\nОбразование\nСообщества",
                "ФИО и цель\nСписок ключевых компетенций\nВклады в продукт\nОбразование и курсы\nПубликации/выступления",
            ],
            "cover_templates": [
                "Обращение\nПроблема заказчика -> ваш опыт её решать\nПример метрики\nПризыв созвониться",
                "Структура STAR: ситуация, задача, действия, результат -> связь с вакансией",
            ],
        },
        "Продукт и маркетинг": {
            "resume_examples": [
                "Product manager: discovery, A/B тесты, рост MAU на 18%.",
                "Product marketing: go-to-market план, сегментация, рост конверсии лендинга.",
                "Growth specialist: CRM-воронки, эксперименты, автоматизация рассылок.",
            ],
            "cover_examples": [
                "Письмо: что понравилось в продукте и какую гипотезу кандидат готов проверить.",
                "Письмо: опыт работы с кросс-функциональными командами, упоминание цикла PDCA.",
                "Письмо: история пользователя и предложение по улучшению, которое кандидат уже проверил.",
            ],
            "resume_templates": [
                "ФИО | роль\nSummary\nКлючевые достижения (цифры)\nОпыт (продукты, метрики)\nНавыки\nОбразование",
                "ФИО, контакты\nМиссия кандидата\nОпыт product discovery/delivery\nИнструменты\nСофт-скиллы\nХобби",
            ],
            "cover_templates": [
                "Hook про рынок\n2-3 маркера экспертизы\nПредложение эксперимента\nCTA",
                "Почему компания\nКейс из опыта (результат)\nКак поможет продукту\nПожелание связаться",
            ],
        },
    }

    _RESUME_SECTIONS = ["summary", "навык", "опыт", "проекты", "образование", "контакты"]

    _RED_FLAGS = [
        "без оплаты",
        "неоплачиваем",
        "24/7",
        "оплата по результату испытательного срока",
        "многозадачность без границ",
        "требуем круглосуточно",
        "штрафы за опоздания",
        "свой ноутбук обязателен без компенсации",
        "нет договора",
    ]
    _GREEN_SIGNALS = [
        "ментор",
        "оплачиваемая стажировка",
        "гибкий график",
        "medстраховка",
        "индивидуальный план развития",
        "официальное оформление",
        "review процесса",
        "компенсация обучения",
    ]

    def provide_templates(self, group: str | None = None) -> List[TemplateResult]:
        if group:
            return [self._build_result(group)]
        return [self._build_result(name) for name in self._PROJECT_GROUPS]

    def analyze_document(self, text: str, doc_type: str) -> Dict[str, List[str]]:
        normalized = text.lower()
        findings: Dict[str, List[str]] = {
            "структура": [],
            "содержание": [],
            "редактура": [],
            "переформулировки": [],
        }

        missing_sections = [section for section in self._RESUME_SECTIONS if section not in normalized]
        if missing_sections:
            findings["структура"].append(
                f"Добавь блоки: {', '.join(missing_sections[:3])} (нужны для быстрого сканирования HR)."
            )
        if text.count("\n") < 5:
            findings["структура"].append("Добавь разбивку на блоки и списки — сплошной текст тяжело читать.")

        if len(text) < 600:
            findings["содержание"].append("Документ кажется коротким: раскрой 2-3 достижения с цифрами.")
        if "я занимался" in normalized:
            findings["содержание"].append("Заменяй формулировку 'я занимался' на активные глаголы и конкретику.")
        if normalized.count("responsible") > 0:
            findings["содержание"].append("Слово 'responsible' лучше заменить на результат (например, 'увеличил').")

        double_spaces = "  " in text
        if double_spaces:
            findings["редактура"].append("Есть двойные пробелы — пройдись автоформатированием.")
        if any(char.islower() and text[idx - 2 : idx].endswith(". ") for idx, char in enumerate(text)):
            findings["редактура"].append("Начинай предложения с заглавной буквы.")
        if not text.strip().endswith((".", "!", "?")):
            findings["редактура"].append("Добавь финальную точку/призыв — завершение сейчас обрывается.")

        findings["переформулировки"].extend(
            [
                "Вместо 'участвовал в проекте' -> 'Скоординировал релиз фичи, сократил TTM на 20%'.",
                "Добавь метрики: пользователи, конверсия, скорость, качество.",
            ]
        )

        if doc_type.lower().startswith("cover"):
            findings["содержание"].append("Сопроводительное письмо должно отвечать на 'почему компания' и 'почему вы'.")
            findings["переформулировки"].append(
                "Свяжи опыт с задачами вакансии: 'Мой опыт оптимизации CRM поможет вашим процессам продаж'."
            )

        return findings

    def analyze_vacancy(self, text: str) -> Dict[str, List[str] | str]:
        normalized = text.lower()
        red = [flag for flag in self._RED_FLAGS if flag in normalized]
        green = [flag for flag in self._GREEN_SIGNALS if flag in normalized]

        comment_parts: List[str] = []
        if red:
            comment_parts.append("Проверь детали оффера и попроси подтвердить условия письменно.")
        if "без опыта" in normalized and "высокая ответственность" in normalized:
            comment_parts.append("Комбинация 'без опыта' и высокой ответственности — уточни поддержку команды.")
        if not red and not green:
            comment_parts.append("Текст нейтральный: уточни процесс интервью и ожидания к первым 3 месяцам.")

        return {
            "красные флаги": red or ["не найдены явно, смотри детали контракта"],
            "зеленые флаги": green or ["не озвучены — спроси про менторство и оформление"],
            "комментарий": " ".join(comment_parts),
        }

    def _build_result(self, group: str) -> TemplateResult:
        data = self._PROJECT_GROUPS[group]
        return TemplateResult(
            group=group,
            resume_examples=data["resume_examples"],
            cover_examples=data["cover_examples"],
            resume_templates=data["resume_templates"],
            cover_templates=data["cover_templates"],
        )
