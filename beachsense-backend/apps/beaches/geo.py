"""
Small, dependency-free geospatial helpers.

Distances are computed with the Haversine formula (great-circle distance on a
sphere), which is accurate to well under 1% for the short distances this app
cares about (a few km to tens of km). This replaces PostGIS/GDAL so the backend
runs anywhere with plain Python + SQLite/PostgreSQL.
"""

import math

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance in kilometres between two lat/lng points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def beaches_within_radius(queryset, lat, lng, radius_km):
    """
    Returns beaches from `queryset` within `radius_km` of (lat, lng), nearest first.
    A cheap bounding-box filter runs in the database first, so only a handful of
    candidate rows are ever measured precisely in Python.
    """
    lat_delta = radius_km / 111.0
    cos_lat = max(math.cos(math.radians(lat)), 0.01)
    lng_delta = radius_km / (111.0 * cos_lat)

    candidates = queryset.filter(
        latitude__gte=lat - lat_delta, latitude__lte=lat + lat_delta,
        longitude__gte=lng - lng_delta, longitude__lte=lng + lng_delta,
    )

    results = []
    for beach in candidates:
        distance = haversine_km(lat, lng, beach.latitude, beach.longitude)
        if distance <= radius_km:
            beach.distance_km = round(distance, 2)
            results.append(beach)
    results.sort(key=lambda b: b.distance_km)
    return results
