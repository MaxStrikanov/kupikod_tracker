import json
import os
from typing import Any, Dict, Optional


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


class BriefCheckError(Exception):
    pass


def _build_brief_prompt(
    transcript: str,
    description: str,
    duration_seconds: Optional[int],
    integration_start: Optional[int],
    integration_end: Optional[int],
    first_description_line: Optional[str],
) -> str:
    info_parts = []

    if duration_seconds is not None:
        info_parts.append(f"- Общая длительность ролика: {duration_seconds} секунд.")
    if integration_start is not None and integration_end is not None:
        info_parts.append(
            f"- Интеграция по времени: с {integration_start} по {integration_end} секунду."
        )
    if first_description_line:
        info_parts.append(
            f"- Первая строка описания под видео: «{first_description_line}»."
        )
    if description:
        info_parts.append(f"- Полное описание под видео:\n{description}")

    info_block = "\n".join(info_parts) if info_parts else "Дополнительная информация отсутствует."

    return f"""
ТЫ: медиабаинг-специалист Kupikod. Твоя задача — строго проверить рекламную интеграцию на соответствие ТЗ.

ТЗ (сводка требований):

1) Видеочасть:
- Не менее трети интеграции — демонстрация сайта https://steam.kupikod.com (виден сайт, интерфейс, процесс пополнения/покупки).
- Интеграция должна быть в первой трети ролика.
- Хронометраж интеграции не менее 30 секунд.
- В конце интеграции обязательно есть пэкшот (финальный кадр/экран с Kupikod, логотипами и оффером).

2) Озвучка и смысл:
- Обязательно озвучен призыв переходить по ссылке в описании и использовать сервис Kupikod (пополнение Steam/покупка игр).
- Подача активная, энергичная, НЕ монотонное зачитывание.
- Должны быть проговорены основные преимущества подписки Kupikod Premium для пополнения Steam:
  * моментальная оплата и поступление средств;
  * 0% комиссия с подпиской Kupikod Premium;
  * платишь 299 ₽ и пополняешь без комиссий весь месяц;
  * Kupikod несёт ответственность за честность сделки, сервисом уже воспользовались более 25 млн раз.
- Должно быть упоминание БЕСПЛАТНОГО ПРОБНОГО ПЕРИОДА подписки и фраза в духе:
  “А если не верите, что это возможно, то просто оформите бесплатный пробный период на сайте!”
  В момент этой фразы в кадре/субтитрах должен быть дисклеймер:
  “*Имеет ограничения по времени и сумме пополнения. С полными условиями можно ознакомиться в оферте на официальном сайте.”
- Управление подпиской через личный кабинет, всё делается автоматически (смена тарифа, возврат средств и т.д.).

3) Преимущества покупки игр на Kupikod:
- Можно сразу покупать игры (ключом или гифтом), в том числе заблокированные в регионе.
- Большой выбор (новинки и бестселлеры).
- Кэшбек с покупок и регулярные конкурсы.

4) Ссылка в описании:
- Ссылка должна быть первой строкой описания.
- Сначала ссылка, затем короткое описание и промокод.
- Остальной текст и другие ссылки спрятаны под разворот.
- В идеале текст в первой строке в духе:
  “[ТВОЯ ССЫЛКА]: 0% комиссия на пополнение Steam — Kupikod!”
  “Промокод: [ТВОЙ ПРОМОКОД]”
  Плюс ниже ссылки на паблик/канал Kupikod.

ДАННЫЕ КОНКРЕТНОЙ ИНТЕГРАЦИИ:

Информация о ролике:
{info_block}

Транскрипт/текст интеграции:
\"\"\"{transcript}\"\"\"

ТВОЯ ЗАДАЧА:
1. Проанализировать, насколько интеграция соответствует каждому пункту ТЗ.
2. Вернуть СТРОГО один JSON (без пояснений вокруг) такого формата:

{{
  "overall_status": "ok" | "minor_issues" | "fail",
  "summary": "краткое резюме, 1–2 предложения",
  "checks": {{
    "site_demo_third":       {{ "ok": true/false, "comment": "..." }},
    "in_first_third":        {{ "ok": true/false, "comment": "..." }},
    "duration_30s":          {{ "ok": true/false, "comment": "..." }},
    "cta_link_kupikod":      {{ "ok": true/false, "comment": "..." }},
    "packshot":              {{ "ok": true/false, "comment": "..." }},
    "link_first_line":       {{ "ok": true/false, "comment": "..." }},
    "tone_active":           {{ "ok": true/false, "comment": "..." }},
    "premium_benefits":      {{ "ok": true/false, "comment": "..." }},
    "trial_mentioned":       {{ "ok": true/false, "comment": "..." }},
    "trial_disclaimer":      {{ "ok": true/false, "comment": "..." }},
    "subscription_control":  {{ "ok": true/false, "comment": "..." }},
    "games_benefits":        {{ "ok": true/false, "comment": "..." }}
  }},
  "recommended_edits": [
    "правка 1",
    "правка 2"
  ]
}}

Если по какому-то пункту данных нет, ставь "ok": false и в "comment" честно пиши, что информации мало или этого не видно.
НЕ ПИШИ НИЧЕГО КРОМЕ JSON.
"""


def check_brief_with_deepseek(
    transcript: str,
    description: str = "",
    duration_seconds: Optional[int] = None,
    integration_start: Optional[int] = None,
    integration_end: Optional[int] = None,
    first_description_line: Optional[str] = None,
) -> Dict[str, Any]:
    """Вызывает DeepSeek и возвращает распарсенный JSON по чеклисту ТЗ."""
    if not DEEPSEEK_API_KEY:
        raise BriefCheckError("DEEPSEEK_API_KEY не задан в окружении")

    prompt = _build_brief_prompt(
        transcript=transcript,
        description=description,
        duration_seconds=duration_seconds,
        integration_start=integration_start,
        integration_end=integration_end,
        first_description_line=first_description_line,
    )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Ты строгий проверяющий соответствия рекламной интеграции ТЗ Kupikod. Отвечай ТОЛЬКО JSON-объектом.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        # если DeepSeek поддерживает OpenAI-формат response_format — будет идеально;
        # если нет, модель просто вернёт текст, мы его ниже распарсим
        "response_format": {"type": "json_object"},
    }

    url = f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"
    resp = requests.post(url, headers=headers, json=payload, timeout=60)

    if resp.status_code != 200:
        raise BriefCheckError(f"DeepSeek API {resp.status_code}: {resp.text}")

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise BriefCheckError(f"Неожиданный ответ DeepSeek: {data}") from e

    # пробуем сразу как JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # fallback: выдираем JSON из текста
        try:
            start = content.index("{")
            end = content.rindex("}") + 1
            return json.loads(content[start:end])
        except Exception as e:
            raise BriefCheckError(f"Не удалось распарсить JSON из ответа: {content}") from e
