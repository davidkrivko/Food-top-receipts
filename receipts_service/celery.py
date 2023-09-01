import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "receipts_service.settings")

app = Celery("receipts_service")

app.config_from_object("django.conf:settings", namespace="CELERY")
