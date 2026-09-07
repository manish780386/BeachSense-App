from celery import shared_task
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from apps.users.models import User
from apps.beaches.models import Beach
from apps.suitability.models import SuitabilityStatus
from .models import AlertLog
from .services import send_push_notification

ALERT_RADIUS_KM = 15


@shared_task
def check_and_send_alerts():
    """Runs every 15 minutes — finds users with a known location and
    checks whether any nearby beach has turned unsafe, sending a push
    notification if so (and logging it, to avoid duplicate spam)."""

    sent = 0
    users = User.objects.exclude(last_known_latitude=None).exclude(fcm_token=None)

    for user in users:
        user_point = Point(user.last_known_longitude, user.last_known_latitude, srid=4326)
        nearby_beaches = Beach.objects.filter(
            is_active=True,
            location__distance_lte=(user_point, D(km=ALERT_RADIUS_KM)),
        )

        for beach in nearby_beaches:
            latest_status = (
                SuitabilityStatus.objects.filter(beach=beach).order_by("-computed_at").first()
            )
            if not latest_status or latest_status.status == "SUITABLE":
                continue

            already_alerted = AlertLog.objects.filter(
                user=user, beach=beach, sent_at__gte=latest_status.computed_at
            ).exists()
            if already_alerted:
                continue

            message = f"{beach.name} is currently {latest_status.status.replace('_', ' ')}: {latest_status.reason}"
            send_push_notification(user.fcm_token, "Beach Safety Alert", message)
            AlertLog.objects.create(user=user, beach=beach, message=message)
            sent += 1

    return f"Sent {sent} alerts."