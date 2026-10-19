from django.db import models


class Beach(models.Model):
    """Represents a single coastal recreational location."""

    name = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)

    # Plain latitude/longitude (WGS84). Nearby-beach search uses the Haversine
    # formula in apps/beaches/geo.py, so no GDAL/PostGIS install is required.
    latitude = models.FloatField()
    longitude = models.FloatField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["state", "name"]
        indexes = [models.Index(fields=["latitude", "longitude"])]

    def __str__(self):
        return f"{self.name}, {self.state}"
