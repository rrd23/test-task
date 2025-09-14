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
    },
    # Настройки кодировки для корректной работы с UTF-8
    worker_hijack_root_logger=False,
    worker_log_color=False,
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)