from django.urls import path

from analytics_dashboard.views import PublicAnalyticsInfoView

urlpatterns = [
    path("", PublicAnalyticsInfoView.as_view(), name="public-analytics-info"),
]
