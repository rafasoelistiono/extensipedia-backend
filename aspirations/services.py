import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import NotFound

from aspirations.models import AspirationActivityLog, AspirationSubmission
from aspirations.selectors import find_ticket_by_ticket_id

TICKET_ID_PREFIX = "ASP"
TICKET_ID_REGEX = rf"^{TICKET_ID_PREFIX}-[A-F0-9]{{10}}$"


def generate_ticket_id():
    while True:
        ticket_id = f"ASP-{uuid.uuid4().hex[:10].upper()}"
        if not AspirationSubmission.objects.filter(ticket_id=ticket_id).exists():
            return ticket_id


def create_public_aspiration_submission(**validated_data):
    with transaction.atomic():
        validated_data["ticket_id"] = generate_ticket_id()
        aspiration = AspirationSubmission.objects.create(**validated_data)
        create_activity_log(
            aspiration,
            action=AspirationActivityLog.Action.SUBMITTED,
            message="Aspiration ticket submitted",
            actor_name=aspiration.full_name,
            metadata={"source": "public_form"},
        )
    send_aspiration_confirmation_email(aspiration)
    return aspiration


def send_aspiration_confirmation_email(aspiration):
    subject = f"Aspiration ticket {aspiration.ticket_id}"
    message = (
        f"Hello {aspiration.full_name},\n\n"
        f"Your aspiration has been received.\n"
        f"Ticket ID: {aspiration.ticket_id}\n"
        f"Title: {aspiration.title}\n"
        f"Status: {aspiration.get_status_display()}\n\n"
        "Please keep this ticket ID to track progress."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_list=[aspiration.email],
        fail_silently=False,
    )


def increment_upvote(aspiration):
    AspirationSubmission.objects.filter(pk=aspiration.pk).update(upvote_count=F("upvote_count") + 1)
    aspiration.refresh_from_db()
    return aspiration


def increment_vote(aspiration):
    AspirationSubmission.objects.filter(pk=aspiration.pk).update(vote_count=F("vote_count") + 1)
    aspiration.refresh_from_db()
    return aspiration


def set_featured_state(aspiration, *, is_featured):
    aspiration.is_featured = is_featured
    aspiration.save()
    create_activity_log(
        aspiration,
        action=AspirationActivityLog.Action.FEATURED if is_featured else AspirationActivityLog.Action.UNFEATURED,
        message="Aspiration featured on homepage" if is_featured else "Aspiration removed from homepage",
        actor_name=getattr(aspiration.updated_by, "full_name", "") if aspiration.updated_by else "",
        metadata={"is_featured": is_featured},
    )
    return aspiration


def is_valid_ticket_id_format(ticket_id):
    import re

    return bool(ticket_id and re.fullmatch(TICKET_ID_REGEX, ticket_id))


def get_ticket_for_public_tracking(ticket_id):
    if not is_valid_ticket_id_format(ticket_id):
        raise NotFound("Ticket not found.")

    aspiration = find_ticket_by_ticket_id(ticket_id)
    if aspiration is None:
        raise NotFound("Ticket not found.")

    return aspiration


def create_activity_log(aspiration, *, action, message, actor_name="", metadata=None):
    return AspirationActivityLog.objects.create(
        aspiration=aspiration,
        action=action,
        message=message,
        actor_name=actor_name,
        status_snapshot=aspiration.status,
        visibility_snapshot=aspiration.visibility,
        metadata=metadata or {},
    )


def update_aspiration_submission(aspiration, validated_data, actor):
    changed_fields = []
    tracked_fields = {"status", "visibility", "is_featured", "title", "short_description"}

    for field, value in validated_data.items():
        if getattr(aspiration, field) != value:
            if field in tracked_fields:
                changed_fields.append(field)
            setattr(aspiration, field, value)

    aspiration.updated_by = actor
    aspiration.save()

    if changed_fields:
        create_activity_log(
            aspiration,
            action=AspirationActivityLog.Action.UPDATED,
            message="Aspiration ticket updated",
            actor_name=getattr(actor, "full_name", "") or getattr(actor, "email", ""),
            metadata={"changed_fields": changed_fields},
        )

    return aspiration
