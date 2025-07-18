import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
app = Celery('dream_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'upload-logs-daily': {
        'task': 'common.utils.upload_logs.upload_logs_to_s3',
        'schedule': crontab(hour=0, minute=0)
    }
}
