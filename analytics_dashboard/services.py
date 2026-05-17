import hashlib

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F

from analytics_dashboard.models import ActivityEvent, ActivityEventCounter
from analytics_dashboard.selectors import get_dashboard_summary_metrics, get_recent_ticket_activity_logs


def build_dashboard_summary():
    return get_dashboard_summary_metrics()


def build_recent_ticket_log(limit=20):
    return get_recent_ticket_activity_logs(limit=limit)


def record_public_activity_event(validated_data, request):
    action_key = validated_data["action_key"]
    idempotency_key = validated_data.get("idempotency_key")

    if idempotency_key:
        existing_event = get_existing_activity_event(action_key, idempotency_key)
        if existing_event:
            return build_activity_event_result(existing_event.counter)

    request_context = build_activity_request_context(request)

    try:
        with transaction.atomic():
            counter, _ = ActivityEventCounter.objects.select_for_update().get_or_create(action_key=action_key)
            ActivityEvent.objects.create(
                counter=counter,
                action_key=action_key,
                label=validated_data["label"],
                page_path=validated_data["page_path"],
                target_type=validated_data["target_type"],
                target_id=validated_data.get("target_id"),
                target_url=validated_data.get("target_url"),
                metadata=validated_data.get("metadata") or {},
                idempotency_key=idempotency_key,
                created_by=request.user if getattr(request.user, "is_authenticated", False) else None,
                updated_by=request.user if getattr(request.user, "is_authenticated", False) else None,
                **request_context,
            )
            ActivityEventCounter.objects.filter(pk=counter.pk).update(total_count=F("total_count") + 1)
            counter.refresh_from_db(fields=["total_count"])
    except IntegrityError:
        existing_event = get_existing_activity_event(action_key, idempotency_key)
        if existing_event:
            return build_activity_event_result(existing_event.counter)
        raise

    return build_activity_event_result(counter)


def get_existing_activity_event(action_key, idempotency_key):
    if not idempotency_key:
        return None
    return (
        ActivityEvent.objects.select_related("counter")
        .filter(action_key=action_key, idempotency_key=idempotency_key)
        .first()
    )


def build_activity_event_result(counter):
    return {
        "action_key": counter.action_key,
        "total_count": counter.total_count,
    }


def build_activity_request_context(request):
    session_key = ""
    if hasattr(request, "session"):
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key or ""

    user_hash = ""
    if getattr(request.user, "is_authenticated", False):
        user_hash = make_privacy_hash(str(request.user.pk))

    return {
        "session_key": session_key,
        "user_hash": user_hash,
        "ip_hash": make_privacy_hash(get_client_ip(request)),
        "user_agent": request.META.get("HTTP_USER_AGENT", "").strip()[:1000],
    }


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def make_privacy_hash(value):
    if not value:
        return ""
    raw = f"{settings.SECRET_KEY}:{value}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
