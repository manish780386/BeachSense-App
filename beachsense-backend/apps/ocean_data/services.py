"""
Data ingestion layer.

REAL DATA SOURCE: Open-Meteo Marine + Weather APIs.
- Free, no API key required, no signup, no rate-limit issues for a student project.
- Provides genuine forecast-model-derived wave height, ocean current speed and
  wind speed for any latitude/longitude worldwide, including Indian beaches.
- Docs: https://open-meteo.com/en/docs/marine-weather-api
        https://open-meteo.com/en/docs/

LIMITATION (be upfront about this with your guide):
- Water Quality Index has no free, real-time, beach-level public API for India,
  so it stays simulated for now (clearly flagged as such below).
- Tsunami/Storm Surge alerts are issued irregularly by INCOIS with no clean
  real-time feed, so they default to False here — wire up an admin toggle or
  the INCOIS bulletin page once your team gets formal INCOIS access.
"""

import random
import requests

MARINE_API_URL = "https://marine-api.open-meteo.com/v1/marine"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_mock_reading(beach):
    """Fallback generator — used only if the real API call fails
    (e.g. no internet, or the marine model has no data for that exact point)."""
    wave_height = round(random.uniform(0.3, 3.5), 2)
    wind_speed = round(random.uniform(5, 55), 1)
    current_speed = round(random.uniform(0, 12), 1)

    return {
        "wave_height_m": wave_height,
        "wind_speed_kmph": wind_speed,
        "current_speed_kmph": current_speed,
        "water_quality_index": round(random.uniform(50, 100), 1),  # simulated — no real source available
        "tsunami_alert": False,
        "storm_surge_alert": False,
        "high_wave_alert": wave_height > 2.5,
        "source": "MOCK_FALLBACK",
    }


def fetch_real_reading(beach):
    """Pulls genuine current ocean/weather conditions for the beach's
    coordinates from Open-Meteo (no API key needed)."""

    lat, lng = beach.location.y, beach.location.x

    marine_resp = requests.get(
        MARINE_API_URL,
        params={
            "latitude": lat,
            "longitude": lng,
            "current": "wave_height,ocean_current_velocity",
            "timezone": "auto",
        },
        timeout=8,
    )
    marine_resp.raise_for_status()
    marine_data = marine_resp.json().get("current", {})

    weather_resp = requests.get(
        WEATHER_API_URL,
        params={
            "latitude": lat,
            "longitude": lng,
            "current": "wind_speed_10m",
            "timezone": "auto",
        },
        timeout=8,
    )
    weather_resp.raise_for_status()
    weather_data = weather_resp.json().get("current", {})

    wave_height = marine_data.get("wave_height")
    current_velocity_ms = marine_data.get("ocean_current_velocity")  # metres/sec
    wind_speed_kmph = weather_data.get("wind_speed_10m")  # already km/h by default

    # Near-shore points sometimes fall outside the marine model's grid coverage
    # and come back as null — fall back to mock data rather than crash.
    if wave_height is None or wind_speed_kmph is None:
        return fetch_mock_reading(beach)

    current_speed_kmph = (current_velocity_ms or 0) * 3.6  # m/s -> km/h

    return {
        "wave_height_m": round(wave_height, 2),
        "wind_speed_kmph": round(wind_speed_kmph, 1),
        "current_speed_kmph": round(current_speed_kmph, 1),
        "water_quality_index": round(random.uniform(50, 100), 1),  # simulated — no real source available
        "tsunami_alert": False,       # no real-time feed available yet — see note above
        "storm_surge_alert": False,   # no real-time feed available yet — see note above
        "high_wave_alert": wave_height > 2.5,
        "source": "OPEN_METEO",
    }


def fetch_reading_for_beach(beach):
    """
    Entry point used by the Celery task.
    Tries the real Open-Meteo APIs first; silently falls back to mock data
    only if the request fails, so the pipeline never breaks in a demo.
    """
    try:
        return fetch_real_reading(beach)
    except (requests.RequestException, ValueError, KeyError):
        return fetch_mock_reading(beach)