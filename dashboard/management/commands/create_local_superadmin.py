from django.core.management.base import BaseCommand

from dashboard.services import ensure_local_development_superuser


class Command(BaseCommand):
    help = "Create the local development superuser used by the custom admin dashboard."

    def handle(self, *args, **options):
        user = ensure_local_development_superuser()
        if user is None:
            self.stdout.write(self.style.WARNING("Skipped local development superuser creation."))
            return
        self.stdout.write(self.style.SUCCESS(f"Local development superuser ready: {user.email}"))
