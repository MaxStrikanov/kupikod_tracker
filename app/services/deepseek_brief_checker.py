import os
import httpx
import json
from typing import Optional, Dict, Any

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


class BriefCheckError(Exception):
    pass


def build_brief_prompt(
    transcript: str,
    description: str,
    duration_seconds: Optional[int],
    integration_start: Optional[int],
    integration_end: Optional[int],
    first_description_line: Optional[str],
) -> str:
    return f"""Ты помощник по рекламе Kupikod. Проверь соответствие ТЗ и верни JSON.

Транскрипт:
{transcript}

Описание:
{description}

Длительность: {duration_seconds}
Интеграция: {integration_start}–{integration_end}
Первая строка описания: {first_description_line}

Структура JSON:
{{
  "overall_status": "ok" | "minor_issues" | "fail",
  "summary": "...",
  "checks": {{
    "position_in_video": {{"ok": bool, "comment": "..."}}, 
    "duration": {{"ok": bool, "comment": "..."}}, 
    "site_demo": {{"ok": bool, "comment": "..."}}, 
    "cta_and_link": {{"ok": bool, "comment": "..."}}, 
    "packshot": {{"ok": bool, "comment": "..."}}, 
    "trial_mention": {{"ok": bool, "comment": "..."}}, 
    "tone_and_delivery": {{"ok": bool, "comment": "..."}}
  }},
  "recommended_edits": ["..."]
}}
Без комментариев вокруг, только JSON.
"""


def _extract_json_block(text: str) -> str:
    """
    DeepSeek любит заворачивать ответ в ```json ... ``` и/или добавлять текст вокруг.
    Тут достаём чистый JSON: от первой { до последней }.
    """
    original = text
    text = text.strip()

    # если есть тройные кавычки — берём кусок между ними, где есть фигурные скобки
    if "```" in text:
        parts = text.split("```")
        candidates = [p for p in parts if "{" in p and "}" in p]
        if candidates:
            text = candidates[0].strip()

    # иногда в начале остаётся "json\n{...}"
    if text.lower().startswith("json"):
        brace = text.find("{")
        if brace != -1:
            text = text[brace:]

    # обрезаем всё до первой { и после последней }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    return text.strip()


def check_brief_with_deepseek(
    transcript: str,
    description: str,
    duration_seconds: Optional[int],
    integration_start: Optional[int],
    integration_end: Optional[int],
    first_description_line: Optional[str],
) -> Dict[str, Any]:
    if not DEEPSEEK_API_KEY:
        raise BriefCheckError("DEEPSEEK_API_KEY is not set")

    prompt = build_brief_prompt(
        transcript,
        description,
        duration_seconds,
        integration_start,
        integration_end,
        first_description_line,
    )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты строгий рекламный продюсер Kupikod."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    resp = httpx.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
    if resp.status_code >= 400:
        raise BriefCheckError(f"DeepSeek HTTP {resp.status_code}: {resp.text}")

    content = resp.json()["choices"][0]["message"]["content"]

    try:
        clean = _extract_json_block(content)
        return json.loads(clean)
    except Exception as e:
        # логируем кусок, чтобы понимать, что пришло
        raise BriefCheckError(
            f"JSON parse error: {e!r}, content: {content[:300]}"
        )
