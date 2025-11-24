import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app = Celery("kupikod", broker=broker_url)
