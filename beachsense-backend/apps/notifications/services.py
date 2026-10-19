"""
Push-notification wrapper using the Firebase Admin SDK (the legacy FCM
"Server Key" was deprecated by Google in June 2024 for all new projects,
so this uses a Service Account JSON credential instead).

One-time setup:
1. Firebase Console -> Project Settings -> Service Accounts
2. Click "Generate New Private Key" -> downloads a .json file
3. Save it as: beachsense-backend/secrets/firebase-service-account.json
   (the "secrets" folder is already in .gitignore - never commit this file)
4. That's it - this module picks it up automatically via FIREBASE_CREDENTIALS_PATH
   in settings.py. No key needs to be copy-pasted into .env.
"""

import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_firebase_app = None  # lazily initialised, cached after first use


def _get_firebase_app():
    """Initialises the Firebase Admin SDK exactly once per process."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    import firebase_admin
    from firebase_admin import credentials

    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    if not os.path.exists(cred_path):
        logger.warning(
            "Firebase service account file not found at %s — "
            "push notifications will be skipped until it is added.",
            cred_path,
        )
        return None

    cred = credentials.Certificate(cred_path)
    _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def send_push_notification(fcm_token, title, body):
    """
    Sends a push notification to a single device token.
    Returns the FCM message ID on success, or None if Firebase isn't
    configured yet or the token is missing — callers should treat None
    as "skipped", not as an error, so the alert pipeline never crashes
    just because notifications aren't set up yet.
    """
    if not fcm_token:
        return None

    app = _get_firebase_app()
    if app is None:
        return None

    from firebase_admin import messaging

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=fcm_token,
    )

    try:
        return messaging.send(message, app=app)
    except Exception as exc:  # noqa: BLE001 — log and continue, never break the alert task
        logger.error("Failed to send push notification: %s", exc)
        return None
