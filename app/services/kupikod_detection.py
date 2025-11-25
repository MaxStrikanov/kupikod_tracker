import re


def detect_kupikod_in_text(raw_text: str) -> bool:
    """Грубый детектор упоминаний Kupikod / Купикод в тексте транскрипта."""
    if not raw_text:
        return False

    text = raw_text.lower()

    # убираем пробелы и знаки для "сплющенного" поиска
    normalized = re.sub(r"[^a-zа-я0-9]", "", text)

    # варианты, которые часто получаются у Whisper
    patterns_norm = [
        "kupikod",
        "купикод",
        "купикупод",
        "купикуод",
        "kupicode",
    ]

    for p in patterns_norm:
        if p in normalized:
            return True

    # паттерн "купи ... код" с любой ерундой между словами
    if re.search(r"купи\W*код", text):
        return True

    # домены/бренд
    domain_keywords = [
        "kupikod.com",
        "steam.kupikod.com",
        "kupikod premium",
        "купикод премиум",
    ]
    if any(k in text for k in domain_keywords):
        return True

    return False
