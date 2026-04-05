from django.db.models.signals import post_migrate
from django.dispatch import receiver

from competency.services import ensure_winner_slide_slots


@receiver(post_migrate)
def ensure_default_winner_slide_slots(sender, app_config, using, **kwargs):
    if app_config is None or app_config.name != "competency":
        return
    ensure_winner_slide_slots(using=using)
