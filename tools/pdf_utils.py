"""Helpers for extracting and shortening PDF documents."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader


def extract_text_from_pdf(path: Path) -> str:
    """Extracts raw text from a PDF file."""

    reader = PdfReader(str(path))
    text_parts: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            text_parts.append(text.strip())
    return "\n".join(text_parts)


def summarize_chunks(chunks: Iterable[str], max_chars: int = 2000) -> str:
    """Utility to limit the size of aggregated PDF excerpts."""

    buffer: List[str] = []
    total = 0
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        if total + len(chunk) > max_chars:
            remaining = max_chars - total
            if remaining <= 0:
                break
            buffer.append(chunk[:remaining])
            break
        buffer.append(chunk)
        total += len(chunk)
    return "\n".join(buffer)
