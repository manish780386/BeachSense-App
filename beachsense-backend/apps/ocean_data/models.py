from django.db import models
from apps.beaches.models import Beach


class OceanParameter(models.Model):
    """A single snapshot of ocean/meteorological readings for a beach,
    sourced from INCOIS (or mock data during development)."""

    beach = models.ForeignKey(Beach, on_delete=models.CASCADE, related_name="ocean_readings")

    wave_height_m = models.FloatField(default=0)
    wind_speed_kmph = models.FloatField(default=0)
    current_speed_kmph = models.FloatField(default=0)
    water_quality_index = models.FloatField(default=100)  # 0 (poor) - 100 (excellent)

    # Critical hazard flags — any True here should force NOT_SUITABLE
    tsunami_alert = models.BooleanField(default=False)
    storm_surge_alert = models.BooleanField(default=False)
    high_wave_alert = models.BooleanField(default=False)

    source = models.CharField(max_length=50, default="INCOIS")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["beach", "-recorded_at"])]

    def __str__(self):
        return f"{self.beach.name} @ {self.recorded_at}"