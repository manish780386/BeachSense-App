from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extends Django's default user with a device token for push
    notifications and an optional last-known location for alerting."""

    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    last_known_latitude = models.FloatField(blank=True, null=True)
    last_known_longitude = models.FloatField(blank=True, null=True)
    location_updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username