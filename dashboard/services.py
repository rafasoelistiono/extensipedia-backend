import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

LOCAL_SUPERADMIN_USERNAME = "superadmin"
LOCAL_SUPERADMIN_PASSWORD = "extensipedia.feb.ui"


def ensure_local_development_superuser():
    if not settings.DEBUG:
        return None

    user_model = get_user_model()

    try:
        user, created = user_model.objects.get_or_create(
            email=LOCAL_SUPERADMIN_USERNAME,
            defaults={
                "full_name": "Superadmin",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
    except (OperationalError, ProgrammingError):
        logger.debug("Skipping local superadmin bootstrap because the database is not ready.")
        return None

    if created:
        # Local development only:
        # These hardcoded credentials are intentionally limited to DEBUG mode.
        # Replace with environment-driven credentials or a dedicated management
        # command/pipeline step in production deployments.
        user.set_password(LOCAL_SUPERADMIN_PASSWORD)
        user.save(update_fields=["password"])
        logger.info("Created local development superuser '%s'.", LOCAL_SUPERADMIN_USERNAME)

    return user

