from django.db import models
from apps.users.models import User
from apps.beaches.models import Beach


class AlertLog(models.Model):
    """Records every push notification sent, so a user is not
    re-notified repeatedly for the same ongoing hazard."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alerts")
    beach = models.ForeignKey(Beach, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]