from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..services.vk_client import VkClient
from ..services.instagram_client import InstagramClient
from ..services.normalizer import normalize_vk_post, normalize_instagram_post
from ..detectors.kupikod import detect_kupikod_integration

from ..schemas import  (
    BriefCheckRequest, 
    BriefCheckResponse,
    BriefCheckRequest,
    BriefCheckResponse,
    LinkCheckRequest,
    LinkCheckResponse,
)
from ..services.deepseek_brief_checker import (
    check_brief_with_deepseek,
    BriefCheckError,
)

from ..services.link_utils import parse_video_link

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/kupikod", response_model=List[schemas.IntegrationRead])
def list_kupikod_integrations(
    db: Session = Depends(get_db),
):
    q = (
        db.query(models.Integration)
        .filter(models.Integration.brand == "kupikod")
        .order_by(models.Integration.detected_at.desc())
        .limit(100)
    )
    return q.all()


@router.post("/kupikod/scan/{blogger_id}", response_model=List[schemas.IntegrationRead])
async def scan_blogger_for_kupikod(
    blogger_id: int,
    days_back: int = 7,
    db: Session = Depends(get_db),
):
    blogger = db.query(models.Blogger).filter(models.Blogger.id == blogger_id).first()
    if not blogger:
        raise HTTPException(status_code=404, detail="Blogger not found")

    since = datetime.utcnow() - timedelta(days=days_back)

    if blogger.platform == "vk":
        if blogger.platform == "instagram":
            client = InstagramClient()
            raw_posts = await client.fetch_posts(blogger.external_id, since=since)
            integrations: List[models.Integration] = []

            for raw in raw_posts:
                existing = (
                    db.query(models.Post)
                    .filter(
                        models.Post.platform == "instagram",
                        models.Post.external_id == str(raw.get("id")),
                        models.Post.blogger_id == blogger.id,
                    )
                    .first()
                )
                if existing:
                    post = existing
                else:
                    norm = normalize_instagram_post(raw, blogger_id=blogger.id)
                    post = models.Post(**norm)
                    db.add(post)
                    db.commit()
                    db.refresh(post)

                post_read = schemas.PostRead.model_validate(post)
                det = detect_kupikod_integration(post_read)
                if not det["brand"]:
                    continue

                integ = (
                    db.query(models.Integration)
                    .filter(models.Integration.post_id == post.id)
                    .first()
                )
                if not integ:
                    integ = models.Integration(
                        post_id=post.id,
                        brand=det["brand"],
                        is_ad=det["is_ad"],
                        confidence=det["confidence"],
                        promo_codes=det["promo_codes"],
                        has_logo=det["has_logo"],
                        has_ad_label=det["has_ad_label"],
                    )
                    db.add(integ)
                else:
                    integ.is_ad = det["is_ad"]
                    integ.confidence = det["confidence"]
                    integ.promo_codes = det["promo_codes"]

                db.commit()
                db.refresh(integ)
                integrations.append(integ)
            return integrations

        client = VkClient()
        raw_posts = await client.fetch_posts(blogger.external_id, since=since)
        integrations: List[models.Integration] = []

        for raw in raw_posts:
            existing = (
                db.query(models.Post)
                .filter(
                    models.Post.platform == "vk",
                    models.Post.external_id == str(raw.get("id")),
                    models.Post.blogger_id == blogger.id,
                )
                .first()
            )
            if existing:
                post = existing
            else:
                norm = normalize_vk_post(raw, blogger_id=blogger.id)
                post = models.Post(**norm)
                db.add(post)
                db.commit()
                db.refresh(post)

            post_read = schemas.PostRead.model_validate(post)
            det = detect_kupikod_integration(post_read)
            if not det["brand"]:
                continue

            integ = (
                db.query(models.Integration)
                .filter(models.Integration.post_id == post.id)
                .first()
            )
            if not integ:
                integ = models.Integration(
                    post_id=post.id,
                    brand=det["brand"],
                    is_ad=det["is_ad"],
                    confidence=det["confidence"],
                    promo_codes=det["promo_codes"],
                    has_logo=det["has_logo"],
                    has_ad_label=det["has_ad_label"],
                )
                db.add(integ)
            else:
                integ.is_ad = det["is_ad"]
                integ.confidence = det["confidence"]
                integ.promo_codes = det["promo_codes"]

            db.commit()
            db.refresh(integ)
            integrations.append(integ)

        return integrations

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Platform {blogger.platform} not implemented yet",
        )

@router.post("/kupikod/{integration_id}/brief-check", response_model=BriefCheckResponse)
def brief_check_integration(
    integration_id: int,
    payload: BriefCheckRequest,
    db: Session = Depends(get_db),
):
    # находим интеграцию, просто чтобы убедиться, что она существует
    integration = (
        db.query(models.Integration)
        .filter(models.Integration.id == integration_id)
        .first()
    )
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    # при желании можно подтягивать описание/метаданные из Post
    description = payload.description or ""
    try:
        result = check_brief_with_deepseek(
            transcript=payload.transcript,
            description=description,
            duration_seconds=payload.duration_seconds,
            integration_start=payload.integration_start,
            integration_end=payload.integration_end,
            first_description_line=payload.first_description_line,
        )
    except BriefCheckError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return BriefCheckResponse(
        overall_status=result.get("overall_status", "fail"),
        summary=result.get("summary", ""),
        checks=result.get("checks", {}),
        recommended_edits=result.get("recommended_edits", []),
        raw=result,
    )
    
@router.post("/kupikod/link-check", response_model=LinkCheckResponse)
def link_check_integration(
    payload: LinkCheckRequest,
    db: Session = Depends(get_db),
):
    """
    Анализ видео по ссылке:
    1) если транскрипт не передан, скачиваем видео и строим транскрипт;
    2) ищем упоминания Kupikod;
    3) если нашли, проверяем соответствие ТЗ через DeepSeek.
    """
    platform, external_id = parse_video_link(payload.url)

    auto_transcript = None
    auto_duration = None

    # если транскрипта нет, пробуем сами его построить
    if not payload.transcript:
        try:
            video_result = analyze_video_from_url(payload.url)
            auto_transcript = video_result.transcript
            auto_duration = video_result.duration_seconds
        except Exception as e:
            print("Video analysis failed:", repr(e))

    transcript = payload.transcript or auto_transcript or ""
    description = payload.description or ""

    # если длительность не передана, берём из анализа
    duration_seconds = payload.duration_seconds or auto_duration

    full_text = f"{transcript}\n{description}".lower()

    kupi_keywords = [
        "kupikod",
        "купи код",
        "купи-код",
        "steam.kupikod.com",
        "steam kupikod",
        "купикод премиум",
    ]
    has_integration = any(k in full_text for k in kupi_keywords)

    brief_result = None
    if has_integration and transcript.strip():
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
            print("Brief check error:", e)

    return LinkCheckResponse(
        platform=platform,
        external_id=external_id,
        has_kupikod_integration=has_integration,
        brief=brief_result,
    )
