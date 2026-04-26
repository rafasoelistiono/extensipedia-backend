from django.db.models.signals import post_migrate
from django.dispatch import receiver

from dashboard.services import ensure_local_development_dashboard_users


@receiver(post_migrate)
def create_local_development_dashboard_users(sender, **kwargs):
    ensure_local_development_dashboard_users()
