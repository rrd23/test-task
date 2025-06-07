from celery import Celery
from ..config import settings

celery_app = Celery(
    "notification_service",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# ✅ Исправлено: правильное автообнаружение задач
celery_app.autodiscover_tasks([
    'app.tasks.notification_tasks'
])

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        "app.tasks.notification_tasks.*": {"queue": "notifications"}
    }
)