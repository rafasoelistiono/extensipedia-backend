from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from aspirations.models import AspirationActivityLog, AspirationSubmission
from analytics_dashboard.models import VisitorDailyVisit


def get_dashboard_summary_metrics():
    today = timezone.localdate()
    start_date = today - timedelta(days=29)

    submissions_qs = AspirationSubmission.objects.all()
    visitors_qs = VisitorDailyVisit.objects.filter(visit_date__gte=start_date, visit_date__lte=today)

    status_counts = {
        item["status"]: item["count"]
        for item in submissions_qs.values("status").annotate(count=Count("id"))
    }

    visitors_by_day = {
        item["visit_date"]: item["count"]
        for item in visitors_qs.values("visit_date").annotate(count=Count("id"))
    }

    daily_chart = []
    for offset in range(30):
        day = start_date + timedelta(days=offset)
        daily_chart.append(
            {
                "date": day,
                "count": visitors_by_day.get(day, 0),
            }
        )

    return {
        "cards": {
            "total_aspiration_submissions": submissions_qs.count(),
            "status_counts": {
                AspirationSubmission.Status.SUBMITTED: status_counts.get(AspirationSubmission.Status.SUBMITTED, 0),
                AspirationSubmission.Status.INVESTIGATING: status_counts.get(
                    AspirationSubmission.Status.INVESTIGATING, 0
                ),
                AspirationSubmission.Status.RESOLVED: status_counts.get(AspirationSubmission.Status.RESOLVED, 0),
            },
            "total_featured_aspirations": submissions_qs.filter(is_featured=True).count(),
            "total_visitors_last_30_days": visitors_qs.count(),
        },
        "charts": {
            "daily_visitors_last_30_days": daily_chart,
        },
    }


def get_recent_ticket_activity_logs(limit=20):
    return (
        AspirationActivityLog.objects.select_related("aspiration", "created_by", "updated_by")
        .all()[:limit]
    )
