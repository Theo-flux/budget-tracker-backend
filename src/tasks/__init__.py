from celery import Celery

from src.config import Config

celery_app = Celery(
    "worker",
    broker=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/1",
    backend=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/2",
)

celery_app.autodiscover_tasks(["src.tasks"])
