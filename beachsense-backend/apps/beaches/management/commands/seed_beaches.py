import csv
import os
from django.core.management.base import BaseCommand
from apps.beaches.models import Beach


class Command(BaseCommand):
    help = "Bulk-imports beaches from seed_data/beaches.csv"

    def handle(self, *args, **options):
        csv_path = os.path.join("seed_data", "beaches.csv")
        created, skipped = 0, 0

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                _, was_created = Beach.objects.get_or_create(
                    name=row["name"],
                    state=row["state"],
                    defaults={
                        "district": row.get("district", ""),
                        "latitude": float(row["latitude"]),
                        "longitude": float(row["longitude"]),
                    },
                )
                created += 1 if was_created else 0
                skipped += 0 if was_created else 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete — {created} beaches created, {skipped} already existed."
        ))
