from django.core.management.base import BaseCommand

from apps.ocean_data.tasks import fetch_incois_data
from apps.suitability.tasks import compute_all_suitability


class Command(BaseCommand):
    help = (
        "Runs one full data cycle right now, without needing Celery/Redis: "
        "fetches live ocean data for every beach, then computes suitability."
    )

    def handle(self, *args, **options):
        self.stdout.write("Fetching ocean data for all beaches (this can take ~30-60s)...")
        self.stdout.write(self.style.SUCCESS(fetch_incois_data()))
        self.stdout.write(self.style.SUCCESS(compute_all_suitability()))
