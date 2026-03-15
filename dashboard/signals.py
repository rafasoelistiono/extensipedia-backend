from django.db.models.signals import post_migrate
from django.dispatch import receiver

from dashboard.services import ensure_local_development_superuser


@receiver(post_migrate)
def create_local_development_superuser(sender, **kwargs):
    ensure_local_development_superuser()

