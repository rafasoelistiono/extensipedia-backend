from analytics_dashboard.selectors import get_dashboard_summary_metrics, get_recent_ticket_activity_logs


def build_dashboard_summary():
    return get_dashboard_summary_metrics()


def build_recent_ticket_log(limit=20):
    return get_recent_ticket_activity_logs(limit=limit)
