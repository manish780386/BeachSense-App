"""
Thin wrapper around Firebase Cloud Messaging.
Fill in FCM_SERVER_KEY in your .env once the Firebase project is created.
"""

import requests
from django.conf import settings

FCM_URL = "https://fcm.googleapis.com/fcm/send"


def send_push_notification(fcm_token, title, body):
    if not settings.FCM_SERVER_KEY or not fcm_token:
        return None  # silently skip in dev if not configured

    headers = {
        "Authorization": f"key={settings.FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": fcm_token,
        "notification": {"title": title, "body": body},
    }
    response = requests.post(FCM_URL, json=payload, headers=headers, timeout=10)
    return response.json()