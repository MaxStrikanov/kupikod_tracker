from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..services.vk_client import VkClient
from ..services.instagram_client import InstagramClient
from ..services.normalizer import normalize_vk_post, normalize_instagram_post
from ..detectors.kupikod import detect_kupikod_integration

from ..schemas import (
    LinkCheckRequest,
    LinkCheckResponse,
)
from ..services.link_utils import parse_video_link
from ..services.video_analyzer import analyze_video_from_url, VideoAnalysisError
from ..services.deepseek_brief_checker import (
    check_brief_with_deepseek,
    BriefCheckError,
)
from typing import List, Dict, Any
from ..services.kupikod_detection import detect_kupikod_in_text

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/kupikod/link-check", response_model=LinkCheckResponse)
def link_check_integration(
    payload: LinkCheckRequest,
    db: Session = Depends(get_db),
):
    """
    Анализ видео по ссылке:
    1) если транскрипт не передан - пытаемся скачать видео и построить транскрипт;
    2) ищем упоминания Kupikod;
    3) если нашли - проверяем ТЗ через DeepSeek.
    """
    platform, external_id = parse_video_link(payload.url)

    transcript = (payload.transcript or "").strip()
    description = payload.description or ""
    duration_seconds = payload.duration_seconds

    # если транскрипт пустой - пробуем получить его автоматически из видео
    if not transcript:
        try:
            video_result = analyze_video_from_url(payload.url)
            transcript = video_result.transcript
            if not duration_seconds:
                duration_seconds = video_result.duration_seconds
        except VideoAnalysisError as e:
            # честно говорим фронту, что именно пошло не так
            raise HTTPException(status_code=400, detail=str(e))

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Не удалось получить текст интеграции из видео. Попробуйте добавить транскрипт вручную.",
        )

    # ищем упоминание Kupikod в тексте
    full_text = f"{transcript}\n{description}"
    has_integration = detect_kupikod_in_text(full_text)

    brief_result = None
    if has_integration:
        try:
            brief_result = check_brief_with_deepseek(
                transcript=transcript,
                description=description,
                duration_seconds=duration_seconds,
                integration_start=payload.integration_start,
                integration_end=payload.integration_end,
                first_description_line=payload.first_description_line,
            )
        except BriefCheckError as e:
            # логируем, но ручку не роняем
            print("Brief check error:", e)

    return LinkCheckResponse(
        platform=platform,
        external_id=external_id,
        has_kupikod_integration=has_integration,
        brief=brief_result,
    )

@router.get("/kupikod")
def list_kupikod_integrations(db: Session = Depends(get_db)):
    """
    Список всех найденных интеграций Kupikod с привязанными постами.

    Формат под фронт:
    [
      {
        "id": ...,
        "is_ad": ...,
        "confidence": ...,
        "promo_codes": [...],
        "detected_at": "...",
        "brief_check": {...} или null,
        "post": {
           "id": ...,
           "blogger_id": ...,
           "platform": "...",
           "external_id": "...",
           "text": "...",
           "published_at": "..."
        }
      },
      ...
    ]
    """
    q = (
        db.query(models.KupikodIntegration)
        .join(models.Post)
        .order_by(models.KupikodIntegration.detected_at.desc())
    )
    rows = q.all()

    result: List[Dict[str, Any]] = []
    for integ in rows:
        post = integ.post
        if not post:
            continue

        post_data: Dict[str, Any] = {
            "id": post.id,
            "blogger_id": post.blogger_id,
            "platform": post.platform,
            "external_id": post.external_id,
            "text": post.text,
            "published_at": post.published_at,
        }

        result.append(
            {
                "id": integ.id,
                "is_ad": integ.is_ad,
                "confidence": integ.confidence,
                "promo_codes": integ.promo_codes,
                "detected_at": integ.detected_at,
                "brief_check": integ.brief_check,
                "post": post_data,
            }
        )

    return result