import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")

app = Celery("library_service", broker="redis://localhost")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.enable_utc = False
app.conf.timezone = settings.TIME_ZONE
app.autodiscover_tasks()
