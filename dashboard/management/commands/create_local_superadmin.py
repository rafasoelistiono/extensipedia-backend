from django.core.management.base import BaseCommand

from dashboard.services import ensure_local_development_dashboard_users


class Command(BaseCommand):
    help = "Create the local development dashboard accounts used by the custom admin dashboard."

    def handle(self, *args, **options):
        users = ensure_local_development_dashboard_users()
        user = users.get("superadmin")
        if not user:
            self.stdout.write(self.style.WARNING("Skipped local development dashboard account creation."))
            return
        self.stdout.write(
            self.style.SUCCESS(
                f"Local development dashboard accounts ready ({len(users)} users). "
                f"Primary superadmin: {user.email}"
            )
        )
