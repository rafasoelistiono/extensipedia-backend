from django.core.management.base import BaseCommand

from dashboard.services import ensure_local_development_superuser


class Command(BaseCommand):
    help = "Create the local development dashboard accounts used by the custom admin dashboard."

    def handle(self, *args, **options):
        user = ensure_local_development_superuser()
        if user is None:
            self.stdout.write(self.style.WARNING("Skipped local development dashboard account creation."))
            return
        self.stdout.write(self.style.SUCCESS(f"Local development dashboard accounts ready. Primary superadmin: {user.email}"))
