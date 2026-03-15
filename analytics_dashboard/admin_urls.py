from django.urls import path

from analytics_dashboard.views import DashboardSummaryView, TicketLogView

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="admin-dashboard-summary"),
    path("ticket-log/", TicketLogView.as_view(), name="admin-dashboard-ticket-log"),
]
