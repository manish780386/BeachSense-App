from django.db import models
from apps.beaches.models import Beach

STATUS_CHOICES = [
    ("SUITABLE", "Suitable"),
    ("CAUTION", "Caution"),
    ("NOT_SUITABLE", "Not Suitable"),
]


class SuitabilityStatus(models.Model):
    """Stores the computed suitability result for a beach at a point in time."""

    beach = models.ForeignKey(Beach, on_delete=models.CASCADE, related_name="suitability_history")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    score = models.FloatField()
    reason = models.CharField(max_length=255, blank=True)  # e.g. "Tsunami alert active"
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-computed_at"]
        indexes = [models.Index(fields=["beach", "-computed_at"])]

    def __str__(self):
        return f"{self.beach.name}: {self.status} ({self.score})"