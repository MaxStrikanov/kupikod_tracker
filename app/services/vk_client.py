import httpx
from datetime import datetime, timedelta
from typing import List
from .collector_base import SourceClient, RawPost
from ..config import settings


class VkClient(SourceClient):
    BASE_URL = "https://api.vk.com/method/"
    API_VERSION = "5.199"

    def __init__(self):
        if not settings.vk_token:
            raise ValueError(
                "VK_TOKEN не найден. Установи VK_TOKEN в переменные окружения."
            )
        self.token = settings.vk_token

    async def _request(self, method: str, params: dict) -> dict:
        params.update(
            {
                "access_token": self.token,
                "v": self.API_VERSION,
            }
        )

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                self.BASE_URL + method,
                params=params,
            )
            data = response.json()
            if "error" in data:
                raise RuntimeError(f"VK API error: {data['error']}")
            return data["response"]

    async def _fetch_wall(self, owner_id: str, count: int = 100, offset: int = 0):
        return await self._request(
            "wall.get",
            {
                "owner_id": owner_id,
                "count": count,
                "offset": offset,
            },
        )

    async def fetch_posts(
        self, blogger_external_id: str, since: datetime | None = None
    ) -> List[RawPost]:
        if since is None:
            since = datetime.utcnow() - timedelta(days=7)

        all_posts: List[RawPost] = []
        offset = 0
        batch_size = 100

        while True:
            try:
                response = await self._fetch_wall(blogger_external_id, batch_size, offset)
            except RuntimeError as e:
                print("VK API error:", e)
                break

            items = response.get("items", [])
            if not items:
                break

            for item in items:
                ts = item.get("date", 0)
                post_dt = datetime.utcfromtimestamp(ts)
                if post_dt < since:
                    return all_posts
                all_posts.append(RawPost(item))

            offset += batch_size
            if offset > 2000:
                break

        return all_posts
