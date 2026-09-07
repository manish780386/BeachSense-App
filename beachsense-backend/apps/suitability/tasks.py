from celery import shared_task
from apps.beaches.models import Beach
from apps.ocean_data.models import OceanParameter
from .models import SuitabilityStatus
from .engine import calculate_suitability


@shared_task
def compute_all_suitability():
    """Runs shortly after fetch_incois_data — takes each beach's latest
    ocean reading and stores a fresh suitability status."""
    updated = 0
    for beach in Beach.objects.filter(is_active=True):
        latest = OceanParameter.objects.filter(beach=beach).order_by("-recorded_at").first()
        if not latest:
            continue

        reading = {
            "wave_height_m": latest.wave_height_m,
            "wind_speed_kmph": latest.wind_speed_kmph,
            "current_speed_kmph": latest.current_speed_kmph,
            "water_quality_index": latest.water_quality_index,
            "tsunami_alert": latest.tsunami_alert,
            "storm_surge_alert": latest.storm_surge_alert,
            "high_wave_alert": latest.high_wave_alert,
        }
        status, score, reason = calculate_suitability(reading)
        SuitabilityStatus.objects.create(beach=beach, status=status, score=score, reason=reason)
        updated += 1

    return f"Computed suitability for {updated} beaches."