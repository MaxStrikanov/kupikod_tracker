from urllib.parse import urlparse
from typing import Optional, Tuple

def parse_video_link(url: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        parsed = urlparse(url)
    except Exception:
        return None, None
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").strip("/")
    platform: Optional[str] = None
    if "vk.com" in host or "vk.ru" in host or "vkvideo.ru" in host:
        platform = "vk"
    elif "instagram.com" in host:
        platform = "instagram"
    if not path:
        return platform, None
    external_id = path
    return platform, external_id
