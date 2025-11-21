import httpx
from datetime import datetime, timedelta
from typing import List, Optional
from .collector_base import SourceClient, RawPost
from ..config import settings


class InstagramClient(SourceClient):
    """
    Клиент для Instagram через Meta Graph API.

    Ожидает переменные окружения:
    - IG_ACCESS_TOKEN
    - IG_BUSINESS_ACCOUNT_ID

    Сейчас это заготовка: бери и допиливай под свою схему аккаунтов.
    """

    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, access_token: Optional[str] = None, business_account_id: Optional[str] = None):
        self.token = access_token or settings.ig_access_token
        self.business_account_id = business_account_id or settings.ig_business_account_id
        if not self.token or not self.business_account_id:
            raise ValueError("Не заданы IG_ACCESS_TOKEN / IG_BUSINESS_ACCOUNT_ID")

    async def _request(self, path: str, params: dict) -> dict:
        params.update(
            {
                "access_token": self.token,
            }
        )
        url = f"{self.BASE_URL}/{path}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if "error" in data:
                raise RuntimeError(f"Instagram API error: {data['error']}")
            return data

    async def fetch_posts(
        self, blogger_external_id: str, since: datetime | None = None
    ) -> List[RawPost]:
        """
        blogger_external_id можно трактовать как IG user id, если захочешь
        хранить разных авторов. Для MVP используем business_account_id из настроек.
        """
        if since is None:
            since = datetime.utcnow() - timedelta(days=7)

        fields = "id,caption,permalink,media_type,media_url,timestamp"
        path = f"{self.business_account_id}/media"

        all_items: List[RawPost] = []
        params = {"fields": fields, "limit": 50}

        while True:
            data = await self._request(path, params)
            items = data.get("data", [])
            if not items:
                break

            for item in items:
                ts = item.get("timestamp")
                if not ts:
                    continue
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
                if dt < since:
                    return all_items
                all_items.append(RawPost(item))

            paging = data.get("paging", {})
            next_url = paging.get("next")
            if not next_url:
                break
            # упрощённая пагинация: переходим по next как по относительному пути
            if next_url.startswith(self.BASE_URL + "/"):
                path = next_url[len(self.BASE_URL) + 1 :]
            else:
                break
            params = {}

        return all_items
