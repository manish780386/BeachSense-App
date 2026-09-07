"""
Suitability Engine
-------------------
Converts raw ocean/meteorological parameters into a SUITABLE / CAUTION /
NOT_SUITABLE classification using a weighted scoring model, with an
instant override for critical hazard alerts (tsunami / storm surge).

This is intentionally a plain function (no Django imports) so it can be
unit-tested in isolation and reused outside the request/task cycle.
"""


def calculate_suitability(reading):
    """
    reading: dict with keys —
        wave_height_m, wind_speed_kmph, current_speed_kmph,
        water_quality_index, tsunami_alert, storm_surge_alert, high_wave_alert

    Returns: (status: str, score: float, reason: str)
    """

    # 1. Critical alerts override everything else
    if reading.get("tsunami_alert"):
        return "NOT_SUITABLE", 0.0, "Tsunami alert active"
    if reading.get("storm_surge_alert"):
        return "NOT_SUITABLE", 0.0, "Storm surge alert active"

    score = 100.0

    # 2. Weighted deductions per parameter
    wave_height = reading.get("wave_height_m", 0)
    wind_speed = reading.get("wind_speed_kmph", 0)
    current_speed = reading.get("current_speed_kmph", 0)
    water_quality = reading.get("water_quality_index", 100)

    score -= min(wave_height * 15, 40)      # wave height impact, capped
    score -= min(wind_speed * 0.5, 20)      # wind impact, capped
    score -= min(current_speed * 2, 20)     # current impact, capped
    score -= (100 - water_quality) * 0.2    # water quality impact

    score = max(score, 0.0)

    # 3. Classify
    if score >= 70:
        return "SUITABLE", round(score, 1), "Conditions within safe range"
    elif score >= 40:
        return "CAUTION", round(score, 1), "Elevated wave/wind/current conditions"
    else:
        return "NOT_SUITABLE", round(score, 1), "Unsafe ocean/weather conditions"