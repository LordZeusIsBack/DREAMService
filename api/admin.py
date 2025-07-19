from django.contrib import admin
from django_celery_beat.models import PeriodicTasks

# Register your models here.
admin.site.register(PeriodicTasks)
