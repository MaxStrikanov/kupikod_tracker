import asyncio
from datetime import datetime, timedelta

from celery import Celery
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from . import models, schemas
from .services.vk_client import VkClient
from .services.instagram_client import InstagramClient
from .services.normalizer import normalize_vk_post, normalize_instagram_post
from .detectors.kupikod import detect_kupikod_integration


celery_app = Celery(
    "kupikod_tasks",
    broker=settings.celery_broker_url,
)


@celery_app.task
def scan_all_bloggers_kupikod(days_back: int = 7) -> int:
    db: Session = SessionLocal()
    try:
        bloggers = db.query(models.Blogger).all()
        total_integrations = 0

        for blogger in bloggers:
            if blogger.platform not in ("vk", "instagram"):
                continue
            integrations = asyncio.run(_scan_single_blogger(db, blogger, days_back))
            total_integrations += len(integrations)

        return total_integrations
    finally:
        db.close()


async def _scan_single_blogger(db: Session, blogger: models.Blogger, days_back: int):
    since = datetime.utcnow() - timedelta(days=days_back)
    if blogger.platform == "vk":
        client = VkClient()
        raw_posts = await client.fetch_posts(blogger.external_id, since=since)
    else:
        client = InstagramClient()
        raw_posts = await client.fetch_posts(blogger.external_id, since=since)

    integrations: list[models.Integration] = []

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
