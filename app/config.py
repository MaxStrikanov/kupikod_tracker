import os
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://kupikod:kupikod@localhost:5433/kupikod",
    )
    vk_token: str | None = os.getenv("VK_TOKEN")
    ig_access_token: str | None = os.getenv("IG_ACCESS_TOKEN")
    ig_business_account_id: str | None = os.getenv("IG_BUSINESS_ACCOUNT_ID")
    use_ml: bool = os.getenv("USE_ML", "0") == "1"
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")


settings = Settings()
