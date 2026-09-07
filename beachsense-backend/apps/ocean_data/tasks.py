from celery import shared_task
from apps.beaches.models import Beach
from .models import OceanParameter
from .services import fetch_reading_for_beach


@shared_task
def fetch_incois_data():
    """Runs every 30 minutes (see celery_app/celery.py beat schedule).
    Pulls a fresh ocean-state reading for every active beach and stores it."""
    created = 0
    for beach in Beach.objects.filter(is_active=True):
        data = fetch_reading_for_beach(beach)
        OceanParameter.objects.create(beach=beach, **data)
        created += 1
    return f"Stored {created} ocean parameter readings."