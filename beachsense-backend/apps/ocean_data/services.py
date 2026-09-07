"""
Data ingestion layer.

During development (before official INCOIS API/data access is confirmed),
`fetch_mock_reading()` generates realistic-looking sample data so the rest
of the pipeline (suitability engine, API, app) can be built and tested.

Once real INCOIS access is available, replace the body of
`fetch_reading_for_beach()` with an actual HTTP call / parser, keeping the
same return shape so nothing downstream needs to change.
"""

import random


def fetch_mock_reading(beach):
    """Generates a plausible random ocean-state reading for a beach."""
    wave_height = round(random.uniform(0.3, 3.5), 2)
    wind_speed = round(random.uniform(5, 55), 1)
    current_speed = round(random.uniform(0, 12), 1)
    water_quality = round(random.uniform(50, 100), 1)

    return {
        "wave_height_m": wave_height,
        "wind_speed_kmph": wind_speed,
        "current_speed_kmph": current_speed,
        "water_quality_index": water_quality,
        "tsunami_alert": random.random() < 0.01,       # ~1% chance
        "storm_surge_alert": random.random() < 0.03,    # ~3% chance
        "high_wave_alert": wave_height > 2.5,
        "source": "MOCK",
    }


def fetch_reading_for_beach(beach):
    """
    Entry point used by the Celery task.
    Swap this out for a real INCOIS API/scraper call later —
    keep the same dict keys so suitability.py doesn't need changes.
    """
    # TODO: replace with real INCOIS integration once API access is confirmed
    return fetch_mock_reading(beach)