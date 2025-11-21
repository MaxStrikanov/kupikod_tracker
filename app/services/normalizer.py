from datetime import datetime
from typing import List, Dict, Any


def normalize_vk_post(raw: Dict[str, Any], blogger_id: int) -> Dict[str, Any]:
    ts = raw.get("date", int(datetime.utcnow().timestamp()))
    published_at = datetime.utcfromtimestamp(ts)

    text = raw.get("text", "") or ""

    links: List[str] = []
    media: List[str] = []

    attachments = raw.get("attachments") or []
    for att in attachments:
        if att.get("type") == "link":
            url = att.get("link", {}).get("url")
            if url:
                links.append(url)
        if att.get("type") in {"photo", "video"}:
            media.append(att.get(att["type"], {}).get("id", ""))

    return {
        "blogger_id": blogger_id,
        "platform": "vk",
        "external_id": str(raw.get("id")),
        "published_at": published_at,
        "text": text,
        "links": links,
        "media": media,
        "raw": raw,
    }


from datetime import datetime
from typing import Dict, Any, List


def normalize_instagram_post(raw: Dict[str, Any], blogger_id: int) -> Dict[str, Any]:
    ts = raw.get("timestamp")
    if ts:
        published_at = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
    else:
        published_at = datetime.utcnow()

    text = raw.get("caption", "") or ""
    links: List[str] = []
    media: List[str] = []

    if raw.get("media_url"):
        media.append(raw["media_url"])
    if raw.get("permalink"):
        links.append(raw["permalink"])

    return {
        "blogger_id": blogger_id,
        "platform": "instagram",
        "external_id": str(raw.get("id")),
        "published_at": published_at,
        "text": text,
        "links": links,
        "media": media,
        "raw": raw,
    }
