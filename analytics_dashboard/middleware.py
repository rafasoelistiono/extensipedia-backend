import hashlib

from django.core.cache import cache
from django.db.models import F
from django.utils import timezone

from analytics_dashboard.models import VisitorDailyVisit


class PublicVisitorAnalyticsMiddleware:
    cache_window_seconds = 600

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not self.should_track(request, response):
            return response

        visit_date = timezone.localdate()
        fingerprint = self.build_fingerprint(request)
        cache_key = f"visitor:{visit_date.isoformat()}:{fingerprint}"

        if cache.get(cache_key):
            return response

        record, created = VisitorDailyVisit.objects.get_or_create(
            visit_date=visit_date,
            fingerprint_hash=fingerprint,
            defaults={
                "first_path": request.path[:255],
                "last_seen_at": timezone.now(),
            },
        )

        if not created:
            VisitorDailyVisit.objects.filter(pk=record.pk).update(
                hit_count=F("hit_count") + 1,
                last_seen_at=timezone.now(),
            )

        cache.set(cache_key, True, timeout=self.cache_window_seconds)
        return response

    def should_track(self, request, response):
        return (
            request.method in {"GET", "HEAD"}
            and response.status_code < 500
            and request.path.startswith("/api/v1/public/")
            and not request.path.startswith("/api/v1/public/tickets/")
            and not request.path.startswith("/static/")
            and not request.path.startswith("/media/")
        )

    def build_fingerprint(self, request):
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "").strip()
        raw = f"{ip_address}|{user_agent}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
