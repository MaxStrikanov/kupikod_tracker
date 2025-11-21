import re
from typing import List
from ..schemas import PostRead
from ..config import settings
from ..ml.model import KupikodMLClassifier


KUPIKOD_PATTERNS = [
    r"\bkupikod\b",
    r"\bкупи\s*код\b",
    r"\bкупикод\b",
]

PROMO_TRIGGERS = [
    "мой промокод",
    "вводи промокод",
    "по промокоду",
    "введи промокод",
    "получи скидку",
    "скидка",
    "комиссия 0",
    "% комиссии",
    "пополнить стим",
]


def _has_kupikod(text: str, links: List[str]) -> bool:
    lower = text.lower()
    for pattern in KUPIKOD_PATTERNS:
        if re.search(pattern, lower):
            return True
    if any("kupikod" in link.lower() for link in links):
        return True
    return False


def _has_promo_triggers(text: str) -> bool:
    lower = text.lower()
    return any(trigger in lower for trigger in PROMO_TRIGGERS)


def _extract_promo_codes(text: str) -> List[str]:
    lower = text.lower()
    codes: List[str] = []
    for m in re.finditer(r"промокод[^\w]{0,10}([a-zA-Z0-9]{4,12})", lower):
        codes.append(m.group(1).upper())
    tokens = re.findall(r"\b[A-Z0-9]{4,12}\b", text)
    for t in tokens:
        if t not in codes:
            codes.append(t)
    return codes


def detect_kupikod_integration(post: PostRead) -> dict:
    has_kupi = _has_kupikod(post.text or "", post.links or [])
    if not has_kupi:
        return {
            "brand": None,
            "is_ad": False,
            "confidence": 0,
            "promo_codes": [],
            "has_logo": False,
            "has_ad_label": False,
        }

    has_triggers = _has_promo_triggers(post.text or "")
    promo_codes = _extract_promo_codes(post.text or "")

    confidence = 40
    if has_triggers:
        confidence += 30
    if promo_codes:
        confidence += 20

    # при включенном USE_ML корректируем уверенность
    if settings.use_ml:
        clf = KupikodMLClassifier()
        proba = clf.predict_proba(
            {
                "has_kupikod": True,
                "has_promo_triggers": has_triggers,
                "has_promo_codes": bool(promo_codes),
            }
        )
        confidence = int(proba * 100)

    if confidence > 100:
        confidence = 100

    is_ad = has_triggers or bool(promo_codes) or (confidence >= 70)

    return {
        "brand": "kupikod",
        "is_ad": is_ad,
        "confidence": confidence,
        "promo_codes": promo_codes,
        "has_logo": False,
        "has_ad_label": False,
    }
