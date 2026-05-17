from django.db.models import Count, Sum

from aspirations.models import AspirationActivityLog, AspirationSubmission
from analytics_dashboard.models import ActivityEventCounter


def get_dashboard_summary_metrics():
    submissions_qs = AspirationSubmission.objects.all()
    total_activity_events_all_time = ActivityEventCounter.objects.aggregate(total=Sum("total_count"))["total"] or 0

    status_counts = {
        item["status"]: item["count"]
        for item in submissions_qs.values("status").annotate(count=Count("id"))
    }

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
            "total_activity_events_all_time": total_activity_events_all_time,
        },
        "charts": {},
    }


def get_recent_ticket_activity_logs(limit=20):
    return (
        AspirationActivityLog.objects.select_related("aspiration", "created_by", "updated_by")
        .all()[:limit]
    )
