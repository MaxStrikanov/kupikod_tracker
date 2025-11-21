from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class RawPost(dict):
    pass


class SourceClient(ABC):
    @abstractmethod
    async def fetch_posts(
        self, blogger_external_id: str, since: datetime | None = None
    ) -> List[RawPost]:
        raise NotImplementedError
