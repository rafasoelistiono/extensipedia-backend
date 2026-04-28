import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

LOCAL_DASHBOARD_PASSWORD = "extensipedia.feb.ui"

LOCAL_DASHBOARD_USERS = (
    {
        "email": "superadmin",
        "dashboard_username": "superadmin",
        "full_name": "Superadmin",
        "dashboard_access_scope": "full",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "akademik@extensipedia.local",
        "dashboard_username": "akademik",
        "full_name": "Admin Akademik",
        "dashboard_access_scope": "academic",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "email": "kompetensi@extensipedia.local",
        "dashboard_username": "kompetensi",
        "full_name": "Admin Kompetensi",
        "dashboard_access_scope": "competency",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "email": "advokasi@extensipedia.local",
        "dashboard_username": "advokasi",
        "full_name": "Admin Advokasi",
        "dashboard_access_scope": "advocacy",
        "is_staff": True,
        "is_superuser": False,
    },
)

LEGACY_LOCAL_DASHBOARD_USER_EMAILS = ("karir@extensipedia.local",)


def ensure_local_development_dashboard_users():
    if not settings.DEBUG:
        return {}

    user_model = get_user_model()
    created_users = {}

    try:
        for spec in LOCAL_DASHBOARD_USERS:
            user, created = user_model.objects.get_or_create(
                email=spec["email"],
                defaults={
                    "dashboard_username": spec["dashboard_username"],
                    "full_name": spec["full_name"],
                    "dashboard_access_scope": spec["dashboard_access_scope"],
                    "is_staff": spec["is_staff"],
                    "is_superuser": spec["is_superuser"],
                    "is_active": True,
                },
            )
            updated_fields = []
            if not user.dashboard_username:
                user.dashboard_username = spec["dashboard_username"]
                updated_fields.append("dashboard_username")
            if user.dashboard_access_scope != spec["dashboard_access_scope"]:
                user.dashboard_access_scope = spec["dashboard_access_scope"]
                updated_fields.append("dashboard_access_scope")
            if user.is_staff != spec["is_staff"]:
                user.is_staff = spec["is_staff"]
                updated_fields.append("is_staff")
            if user.is_superuser != spec["is_superuser"]:
                user.is_superuser = spec["is_superuser"]
                updated_fields.append("is_superuser")
            if not user.is_active:
                user.is_active = True
                updated_fields.append("is_active")
            if updated_fields:
                user.save(update_fields=updated_fields)

            if created:
                # Local development only:
                # These hardcoded credentials are intentionally limited to DEBUG mode.
                # Replace with environment-driven credentials or a dedicated management
                # command/pipeline step in production deployments.
                user.set_password(LOCAL_DASHBOARD_PASSWORD)
                user.save(update_fields=["password"])
                logger.info("Created local development dashboard user '%s'.", spec["dashboard_username"])

            created_users[spec["dashboard_username"]] = user

        user_model.objects.filter(email__in=LEGACY_LOCAL_DASHBOARD_USER_EMAILS).update(
            dashboard_access_scope="competency",
            is_staff=False,
            is_superuser=False,
            is_active=False,
        )
    except (OperationalError, ProgrammingError):
        logger.debug("Skipping local dashboard user bootstrap because the database is not ready.")
        return {}

    return created_users


def ensure_local_development_superuser():
    return ensure_local_development_dashboard_users().get("superadmin")
