from django.contrib.gis.db import models


class Beach(models.Model):
    """Represents a single coastal recreational location."""

    name = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)

    # Geospatial coordinates (longitude, latitude) — geography=True enables
    # accurate real-world distance calculations (metres) instead of flat-plane math.
    location = models.PointField(geography=True, srid=4326)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["state", "name"]

    def __str__(self):
        return f"{self.name}, {self.state}"