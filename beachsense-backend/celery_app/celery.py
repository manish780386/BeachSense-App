import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("beach_safety")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# --- Scheduled (Celery Beat) tasks ---
app.conf.beat_schedule = {
    "fetch-incois-data-every-30-minutes": {
        "task": "apps.ocean_data.tasks.fetch_incois_data",
        "schedule": crontab(minute="*/30"),
    },
    "compute-suitability-every-30-minutes": {
        "task": "apps.suitability.tasks.compute_all_suitability",
        "schedule": crontab(minute="5,35"),
    },
    "check-location-alerts-every-15-minutes": {
        "task": "apps.notifications.tasks.check_and_send_alerts",
        "schedule": crontab(minute="*/15"),
    },
}