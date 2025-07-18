import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dream_service.settings')
app = Celery('dream_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
